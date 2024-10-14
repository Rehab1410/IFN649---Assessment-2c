# IFN649---Assessment-2c
IoT-Health Monitoring System for Children with Febrile Convulsions

# IFN649 - Assessment 2c: IoT Health Monitoring System

## Overview

This project introduces an innovative IoT-based health monitoring solution aimed at supporting children prone to febrile convulsions. The system integrates **temperature, heart rate**, and **shock detection sensors** into one monitoring setup. Data collected from these sensors is processed using a **Teensy microcontroller** and transmitted via Bluetooth to a **Raspberry Pi**. The Raspberry Pi further processes the data and publishes it to **AWS IoT Core** using MQTT for real-time monitoring via an **AWS CloudWatch dashboard**.

The system provides instant alerts through a **buzzer** and AWS notifications whenever sensor readings cross predefined thresholds, enabling rapid caregiver intervention.
