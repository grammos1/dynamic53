# Based on the work done by Robert Ellegate , Dan Pilch and Sven Flickinger
# Original code available on https://github.com/danpilch/aws-dyndns

import boto3
import requests
import configparser
import argparse
import sys
import os
from pushover import Client

domain = ""
record = ""
zone = ""
profile = ""
ttl = 0
pushover_user=""
pushover_token=""

class AWSDynDns(object):
    def __init__(self, profile):
        self.user=""
        self.secret = ""
        self.ip_service = "http://httpbin.org/ip"
        self.domain = ""
        self.record = ""
        self.ttl = ""
        self.hosted_zone_id = ""
        self.get_settings(profile)
        session = boto3.Session(aws_access_key_id=self.user, aws_secret_access_key=self.secret)
        self.client = session.client('route53domains')
        if self.record:
            self.fqdn = "{0}.{1}".format(self.record, self.domain)
        else:
            self.fqdn = self.domain

    def get_external_ip(self):
        try:
            self.external_ip_request = requests.get(self.ip_service)
            if "," in self.external_ip_request.json()['origin']:
                self.external_ip = self.external_ip_request.json()['origin'].split(',')[0]
            else:
                self.external_ip = self.external_ip_request.json()['origin']
            print("Found external IP: {0}".format(self.external_ip))
        except Exception:
            raise Exception("error getting external IP")

    def get_hosted_zone_id(self):
        try:
            self.hosted_zone_list = self.client.list_hosted_zones_by_name()['HostedZones']
            for zone in self.hosted_zone_list:
                if self.domain in zone['Name']:
                    self.hosted_zone_id = zone['Id'].split('/')[2]
        except Exception:
            raise Exception("error getting hosted zone ID")

    def check_existing_record(self):
        """ Get current external IP address """
        self.get_external_ip()

        """ Check for existing record and if it needs to be modified """
        response = self.client.list_resource_record_sets(
            HostedZoneId=self.hosted_zone_id,
            StartRecordName=self.fqdn,
            StartRecordType='A',
        )

        found_flag = False

        if len(response['ResourceRecordSets']) == 0:
            return found_flag
            #raise Exception("Could not find any records matching domain: {0}".format(self.domain))

        if self.fqdn in response['ResourceRecordSets'][0]['Name']:
            for ip in response['ResourceRecordSets'][0]['ResourceRecords']:
                if self.external_ip == ip['Value']:
                    found_flag = True
                    print ("IP on record:" + ip['Value'] )
        else:
            raise Exception("Cannot find record set for domain: {0}".format(self.fqdn))

        return found_flag

    def update_record(self):
        if not self.hosted_zone_id:
            self.get_hosted_zone_id()

        if self.check_existing_record():
             print("IP is already up to date")
        else:
            print("Updating resource record IP address")
            response = self.client.change_resource_record_sets(
                HostedZoneId=self.hosted_zone_id,
                ChangeBatch={
                    'Comment': 'string',
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': self.fqdn,
                                'Type': 'A',
                                'TTL': self.ttl,
                                'ResourceRecords': [
                                    {
                                        'Value': self.external_ip
                                    },
                                ],
                            }
                        },
                    ]
                }
            )
            print("Status: {}".format(response['ChangeInfo']['Status']))
            try:
                client = Client(self.pushover_user, api_token=self.pushover_token)
                client.send_message("IP address for " + self.record + "." + self.domain + " changed to " + self.external_ip, title="dynamic53")
            except Exception:
                raise Exception("No Pushover Credentials (or incorrect entries in config file). Notification not sent")


    def get_settings(self, section):
        try:
            pathname = os.path.abspath(os.path.dirname(sys.argv[0]))
            config = configparser.ConfigParser()
            config.read(pathname +"/dynamic53.cfg")
            self.domain = config[section]["domain"]
            self.record = config[section]["record"]
            try:
                self.ttl = int(config[section]["ttl"])
            except Exception:
                print ("ttl value in config file is not an integer")
                exit (11)
            self.user = config[section]["user"]
            self.secret = config[section]["secret"]
            try:
                self.pushover_user = config[section]["pushover_user"]
                self.pushover_token = config[section]["pushover_token"]
            except Exception:
                print ("Pushover Values not found")
        except Exception:
            print("Unable to load values from the config file. Check the file exists in the same directory as the script and it has the right format and values")
            exit(10)


if __name__ == "__main__":
    print("Starting ...")
    parser = argparse.ArgumentParser(description="Manage a dynamic home IP address with an AWS hosted route53 domain")
    parser.add_argument(
        "--profile", "-p",
        default='default',
        help="Config profile, as listed in your config file. If missing I will use \'default\' ",
        required=True
    )

    args = parser.parse_args()
    run = AWSDynDns(args.profile)
    run.update_record()
