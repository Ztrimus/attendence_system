'''
-----------------------------------------------------------------------
File: attendence_system/main.py
Creation Time: Sep 2nd 2024, 12:17 pm
Author: Saurabh Zinjad
Developer Email: saurabhzinjad@gmail.com
Copyright (c) 2023-2024 Saurabh Zinjad. All rights reserved | https://github.com/Ztrimus
-----------------------------------------------------------------------
'''

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import geopy.distance
import geocoder

if 'attendences' not in st.session_state:
    st.session_state['attendences'] = pd.DataFrame([], columns=['student_name', 'student_id', 'ip_address', 'timestamp'])
class_lat, class_lon = 33.414621602365465, -111.90984407791874

def get_current_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.latlng
    else:
        return None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two coordinates in kilometers."""
    return geopy.distance.distance((lat1, lon1), (lat2, lon2)).km

def verify_location(student_lat, student_lon, class_lat, class_lon, max_distance_km=0.1):
    """Verify if the student is within the allowed distance from the class location."""
    distance = calculate_distance(student_lat, student_lon, class_lat, class_lon)
    return distance <= max_distance_km

from urllib.request import urlopen
import re as r

def get_ip():
    d = str(urlopen('http://checkip.dyndns.com/').read())

    return r.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(d).group(1)

def main():
    st.title("Location-based Attendance System")

    # Input fields
    student_name = st.text_input("Student Name")
    student_id = st.text_input("Student ID")

    if st.button("Submit Attendance"):
        # Check student device IP
        student_ip = get_ip()
        # Get current location
        student_lat, student_lon = get_current_location()

        if student_ip in st.session_state['attendences']['ip_address'].values:
            st.error("You have already marked your attendance.")
        elif student_lat is None or student_lon is None:
            st.error("Could not acquire location. Please ensure location services are enabled.")
        elif verify_location(student_lat, student_lon, class_lat, class_lon):
            # Record attendance
            new_record = {
                'student_name': student_name,
                'student_id': student_id,
                'ip_address': student_ip,
                'timestamp': datetime.now().isoformat()
            }
            st.session_state['attendences'].loc[len(st.session_state['attendences'])] = new_record
            st.success("Attendance recorded successfully!")
        else:
            st.error("You are not in the classroom. Attendance not recorded.")
            # TODO: Time Expired

    # Display attendance records
    st.dataframe(st.session_state['attendences'])
    
if __name__ == "__main__":
    main()