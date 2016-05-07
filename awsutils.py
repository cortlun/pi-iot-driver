from subprocess import Popen, PIPE
import os
from os.path import expanduser
import urllib
#from Crypto.PublicKey import RSA

class ChildProcessUtils:
    def __init__(self, log_file):
        self.user_home = os.path.expanduser("~")
        self.aws_utils_home = os.path.join(self.user_home, "awsutils")
        self.log_directory = os.path.join(self.aws_utils_home, "logs")
        self.previous_ip_location = os.path.join(self.aws_utils_home, "last_ip.txt")
        self.log_file = log_file
    def spawn_child_process(self, args):
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        if p.returncode == 0:
            return out.decode("utf-8")
        else:
            raise Exception("Error: " + err.decode("utf-8"))

class AwsUtils:
    def __init__(self):
        self.user_home = expanduser("~")
        self.aws_utils_home = os.path.join(self.user_home, "awsutils")
        self.log_directory = os.path.join(self.aws_utils_home, "logs")
        self.previous_ip_location = os.path.join(self.aws_utils_home, "last_ip.txt")
        self.cp_utils = ChildProcessUtils("aws_utils.log")
    def add_user_to_group(self, user_name, group_name):
        return self.cp_utils.spawn_child_process(["aws", "iam", "add-user-to-group", "--user-name", user_name, "--group-name", group_name])
    def attach_policy_to_group(self,policy_arn, group_name):
        return self.cp_utils.spawn_child_process(["aws", "iam", "attach-group-policy", "--policy-arn", policy_arn, "--group-name", group_name])
    def create_access_key(self,user_name):
        return self.cp_utils.spawn_child_process(["aws", "iam", "create-access-key", "--user-name", user_name])
    def create_group(self, group_name):
        return self.cp_utils.spawn_child_process(["aws", "iam", "create-group", "--group-name", group_name])
    def create_key_pair(self, key, key_fingerprint, key_name):
        return self.cp_utils.spawn_child_process(["aws", "ec2", "create-key-pair", "--key-name", key_name, "--key-material", key, "--key-fingerprint", key_fingerprint])
    def create_policy(self,policy_name, policy_document):
        return self.cp_utils.spawn_child_process(["aws", "iam", "create-policy", "--policy-name", policy_name, "--policy-document", policy_document])
    def create_security_group(self,security_group, description):
        return self.cp_utils.spawn_child_process(["aws", "ec2", "create-security-group", "--group-name", security_group, "--description", description])
    def create_user(self,user_name):
        return self.cp_utils.spawn_child_process(["aws", "iam", "create-user", "--user-name", user_name])
    def import_key_pair(self, public_key_location, key_name):
        with open(public_key_location) as public_key:
            keydata = public_key.read()
        return self.cp_utils.spawn_child_process(["aws", "ec2", "import-key-pair", "--key-name", key_name, "--public-key-material", keydata])
    def run_instances(self,image_id, count, instance_type, key_name, security_group):
        return self.cp_utils.spawn_child_process(["aws", "ec2", "run-instances", "--image-id", image_id, "--count", count, "--instance-type", instance_type, "--key-name", key_name, "--security-groups", security_group])
    def revoke_firewall_privelege(self,group_name, port, protocol, ip):
        try:
            return self.cp_utils.spawn_child_process(["aws", "ec2", "revoke-security-group-ingress", "--group-name", group_name, "--protocol", protocol, "--port", port, "--cidr", ip])
        except Exception as e:
            print("Error while trying to revoke firewall privelege: " + str(e))
    def authorize_firewall_privelege(self,group_name, port, protocol):
        previous_ip = self.get_previous_ip()
        ip = self.get_my_current_ip()
        if previous_ip is not None:
            self.revoke_firewall_privelege(group_name, port, protocol, previous_ip)
        self.log_current_ip()
        return self.cp_utils.spawn_child_process(["aws", "ec2", "authorize-security-group-ingress", "--group-name", group_name, "--protocol", protocol, "--port", port, "--cidr", ip])
    def allocate_address(self):
        return self.cp_utils.spawn_child_process(["aws", "ec2", "allocate-address"])
    def associate_address(self, instance_id, elastic_ip):
        return self.cp_utils.spawn_child_process(["aws", "ec2", "associate-address", "--instance-id", instance_id, "--public-ip", elastic_ip])
    def describe_instance_status(self, instance_id):
        return self.cp_utils.spawn_child_process(["aws", "ec2", "describe-instance-status", "--instance-id", instance_id])
    def get_my_current_ip(self):
        return urllib.urlopen("http://checkip.amazonaws.com").read().decode("utf-8").rstrip("\r\n") + "/32"
    def log_current_ip(self):
        if not os.path.exists(self.aws_utils_home):
            os.makedirs(self.aws_utils_home)
        with open(self.previous_ip_location, "w+") as f:
            f.write(self.get_my_current_ip())
    def get_previous_ip(self):
        try:
            lines = list(open(self.previous_ip_location))
            return lines[0]
        except:
            return None

if __name__ == "__main__":
    print("Current ip: " + get_my_current_ip())
    print("Logging current ip." )
    log_current_ip()
    print("Previous ip: " + get_previous_ip())