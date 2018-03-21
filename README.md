# Eventfull

## Summary
Eventfull helps to put visuals to a person’s busy everyday life with a calendar 
view and scheduling created from dhtmlxScheduler library. The app is geared towards 
families and friends who want to keep tabs on each other’s ever changing and busy schedules, 
using personal profiles and text notifications with Twilio’s API.

## Tech Stack
__Frontend:__ Javascript, jQuery, AJax, JSon, Jinja, HTML, CSS Bootstrap <br/>
__Backend:__ Python, Flask, PostgreSQL, SQLAlchemy <br/>
__APIs:__ Twilio <br/>
__Library:__ dhtmlxScheduler <br/>

## Features
Users have a profile like a dashboard, and the database is queried to show their personal information, the different types of events, and their list of friends.
<br>
![alt text](/static/readme_img/readme_profile.png)


 As well as a full calendar view created with customized properties from dhtmlxScheduler library.
 <br>
![alt text](/static/readme_img/readme_calendar.png)


Users can view event pages to events they're invited to for more information.
<br>
![alt text](/static/readme_img/readme_event_page.png)


They are also able to upload images to to the event page, sharing with other users and staying connected.
<br>
![alt text](/static/readme_img/readme_pic_carousal.png)


And whenever a user is invited to an event, or some one befriends them, they get a text message notification, thanks to Twilio's API.
<br>
![alt text](/static/readme_img/Twilio_notification_ex.png)

### Future plans:
- Option for email or text notifications
- Upload background picture for event page
- Commenting, versuse one-off comment

## Disclaimer:
The scheduler library is on a 30 day trial, and will most likely stop working after April 5, 2018
