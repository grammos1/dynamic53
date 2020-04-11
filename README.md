# dynamic53
## Automatically update the IP address of route53 records based on the public ip address of the client 
Based on the work done by **Robert Ellegate** , **DanPilch** and **Sven Flickinger**
Original code available on https://github.com/danpilch/aws-dyndns

dynamic53 removes the requirement for the AWS-CLI to be installed and allows configuration files.

### Python 3 requirements:
* boto3
* requests
* configparser
* argparse

### Other requirements

A config file with the following settings:

**\[Profile Name]**

**domain = example.com**

**record = www**

**ttl = 300**

**user = YourAWSRoleKey**

**secret = AWSSecret**

**pushover_user= userkey**

**pushover_token= tokenkey**


### Usage
python3 dns_update.py [--profile PROFILE]

PROFILE is the section in the config file. if ommited, profile is set to 'default'. The Profile setting is Case Sensitive.
Pushover (https://pushover.net/) credentials are optional and if exist, then a notification will be sent
