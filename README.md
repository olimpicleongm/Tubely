## DESCRIPTION
sync YouTube subscriptions with Feedly

## INSTALLATION
1. service settings  
refresh access token at Feedly (cloud scope)  
get client secrets json file from Google (YouTube Data API)  

1. create config  
~/.Tubely.cfg  
[Tubely]  
youtube_channel_id = <get subscriotions from YouTube channel id\>  
feedly_access_token = <Feedly access token, valid for 30 days - free account limitation\>  
~/.Tubely-youtube.json <YouTube client secrets json file\>  

1. create Feedly folder for subscriptions

1. accept OAuth at first run

1. add to cron (e.g. every 2 hours)  
crontab -e  
0 \*/2 \* \* \* ~/<PATH_TO_SCRIPT\>  

1. check logs  
/var/mail/<user\>