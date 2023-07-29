# Overview
A quick little Python program I wrote up to alert via a MacroDroid notification me when an email comes into my Gmail inbox that contains a designated word.

## Technologies
* Python
* G-Suite (Gmail) APIs
* MacroDroid

## Details
The program is set to check my Gmail inbox every 15 minutes for 8 hours for emails that have "Interview" in the subject line. The program only checks for unread emails, that are not promotional, spam, or related to any social networking services. If no relevant emails containing the trigger word (i.e. "Interview") are found, the program sleeps for another 15 minutes before checking again.

If a relevant email is found, the email's full subject line and from address are stored as a key-value pair. That key-value pair is then send to a unique MacroDroid webhook url, which triggers a macro on my phone that sends me a push notification containing the subject line and the sender's email address.  
