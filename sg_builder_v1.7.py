############################################################
#  AWS SG Builder v1.7                                     #
#  Author: Bobby Williams                                  #
#  Contact: bobby.williams@xxxxxxxx.com                    #
############################################################

import openpyxl, boto3, os, re, time, getpass, sys, warnings 
import subprocess as sp


# Ask for the client's shortname:
print("What's the client's short name? (ex. DUKE, UOP, MAYOC, etc.)")
shortname = raw_input('> ')
shortname = shortname.upper()

# Sheet1 check:
print("Did you copy the entire 'Security Group Rules' sheet and paste the *values to a new sheet named 'Sheet1'? (y/n)")
sheet1_check = raw_input('> ')
while sheet1_check not in 'yYnN':
    print('Invalid selection!')
    print("Did you copy the entire 'Security Group Rules' sheet and paste the *values to a new sheet named 'Sheet1'? (y/n)")
    sheet1_check = raw_input('> ')
if sheet1_check in 'nN':
    print("Sorry, but you need to copy the entire 'Security Group Rules' sheet and paste the *values to a new sheet named 'Sheet1' before continuing")
    print('Exiting...')
    sys.exit()

# Ask for VPC id for SGs:
print("What's the vpc id that SGs will be assigned to?")
vpc_id = raw_input('> ')

# Get region:
print("Choose the Region (pick a letter):")
print('---------------------------------------------------------------')
print("[A]: us-east-1 (Virginia)  |     [H]: eu-west-2 (London)")
print('---------------------------|-----------------------------------')
print("[B]: us-east-2 (Ohio)      |     [I]: ap-northeast-1 (Tokyo)")
print('-----------------|---------|-----------------------------------')
print("[C]: us-west-1 (N. Cali)   |     [J]: ap-northeast-2 (Seoul)")
print('-----------------|---------|-----------------------------------')
print("[D]: us-west-2 (Oregon)    |     [K]: ap-southeast-1 (Singapore)")
print('---------------------------|-----------------------------------')
print("[E]: ca-central-1 (Canada) |     [L]: ap-southeast-2 (Sydney)")
print('---------------------------|-----------------------------------')
print("[F]: eu-west-1 (Ireland)   |     [M]: ap-south-1 (Mumbai)")
print('-----------------------------|---------------------------------')
print("[G]: eu-central-1 (Frankfurt)|   [N]: sa-east-1 (Sao Paulo)")
get_region = raw_input('> ')
while get_region not in 'aAbBcCdDeEfFgGhHiIjJkKlLmMnN':
    print("Invalid selection!")
    print("Choose the Region (pick a letter):")
    print('---------------------------------------------------------------')
    print("[A]: us-east-1 (Virginia)  |     [H]: eu-west-2 (London)")
    print('---------------------------|-----------------------------------')
    print("[B]: us-east-2 (Ohio)      |     [I]: ap-northeast-1 (Tokyo)")
    print('-----------------|---------|-----------------------------------')
    print("[C]: us-west-1 (N. Cali)   |     [J]: ap-northeast-2 (Seoul)")
    print('-----------------|---------|-----------------------------------')
    print("[D]: us-west-2 (Oregon)    |     [K]: ap-southeast-1 (Singapore)")
    print('---------------------------|-----------------------------------')
    print("[E]: ca-central-1 (Canada) |     [L]: ap-southeast-2 (Sydney)")
    print('---------------------------|-----------------------------------')
    print("[F]: eu-west-1 (Ireland)   |     [M]: ap-south-1 (Mumbai)")
    print('-----------------------------|---------------------------------')
    print("[G]: eu-central-1 (Frankfurt)|   [N]: sa-east-1 (Sao Paulo)")
    get_region = raw_input('> ')
if get_region in 'aA':
    region = 'us-east-1'
elif get_region in 'bB':
    region = 'us-east-2'
elif get_region in 'cC':
    region = 'us-west-1'
elif get_region in 'dD':
    region = 'us-west-2'
elif get_region in 'eE':
    region = 'ca-central-1'
elif get_region in 'fF':
    region = 'eu-west-1'
elif get_region in 'gG':
    region = 'eu-central-1'
elif get_region in 'hH':
    region = 'eu-west-2'
elif get_region in 'iI':
    region = 'ap-northeast-1'
elif get_region in 'jJ':
    region = 'ap-northeast-2'
elif get_region in 'kK':
    region = 'ap-southeast-1'
elif get_region in 'lL':
    region = 'ap-southeast-2'
elif get_region in 'mM':
    region = 'ap-south-1'
elif get_region in 'nN':
    region = 'sa-east-1'
    
# Ask for username & password:
print('Provide your login credentials for STS:')
username = raw_input("Username: ")
password = getpass.getpass("Password: ")

# Select STS role:
print('Select a role:')
print('[A]: cloudnetworkops')
print('[B]: classiccloudreadonly')
print('[C]: cloudreadonly')
get_role = raw_input('> ')
if get_role in 'aA':
    role = 'cloudnetworkops'
elif get_role in 'bB':
    role = 'classiccloudreadonly'
elif get_role in 'cC':
    role = 'cloudreadonly'
while get_role not in 'aAbBcC':
    print('Invalid selection!')
    print('Select a role:')
    print('[A]: cloudnetworkops')
    print('[B]: classiccloudreadonly')
    print('[C]: cloudreadonly')
    get_role = raw_input('> ')
    if get_role in 'aA':
        role = 'cloudnetworkops'
    elif get_role in 'bB':
        role = 'classiccloudreadonly'
    elif get_role in 'cC':
        role = 'cloudreadonly'

# Get account for client:
print("Grabbing client's account id...")
account_ls = sp.check_output('sts.exe -list-accounts',shell=True)
accounts = account_ls.splitlines()
if shortname == 'UOP':
    acct_num = '10088'
elif shortname in account_ls:
    for i in accounts:                 
        if shortname in i:
            acct_num = i[:5]
else:
    print('Sorry, but account not found, exiting..')
    sys.exit()
time.sleep(2)        
print("Account id found! -> {}".format(acct_num))

# Select account with sts (with wrong password notification):
print('Selecting account in sts.exe...')
try:
    get_acct = sp.check_output('sts.exe -account={} -user={} -password={} -role={}'.format(acct_num,username,password,role),shell=True)
except:
    print('Error - Check your password, exiting..')
    sys.exit()    

# Set aws environment variables:
print("Setting aws environment variables...")
set_keys = sp.check_output('setaws.bat',shell=True)
time.sleep(2)
    # Grab the access key id:
access_key_id = re.search(r'AWS_ACCESS_KEY_ID=\S+', set_keys).group()
access_key_id = access_key_id.replace('AWS_ACCESS_KEY_ID=', '')
    # Grab the secret access key:
secret_access_key = re.search(r'AWS_SECRET_ACCESS_KEY=\S+', set_keys).group()
secret_access_key = secret_access_key.replace('AWS_SECRET_ACCESS_KEY=', '')
    # Grab the session token:
session_token = re.search(r'AWS_SESSION_TOKEN=\S+', set_keys).group()
session_token = session_token.replace('AWS_SESSION_TOKEN=', '')

# Create Boto3 Client:
print('Logging into AWS...')
conn = boto3.client('ec2',region_name=region,aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,aws_session_token=session_token)
time.sleep(2)
print('Connected!')

#############
# Create SGs:
#############
warnings.filterwarnings('ignore') # Ignore openpyxl UserWarning
wb = openpyxl.load_workbook('{} XXXX CS Server Network Build-AWS.xlsx'.format(shortname))
sgr = wb.get_sheet_by_name('Sheet1')
sg_names = []
sg_descriptions = []
sg_lib = {}
for i in range(4,500):
    if sgr['C{}'.format(i)].value == None:
        continue
    else: 
        sg_name = sgr['C{}'.format(i)].value
        sg_description = sgr['A{}'.format(i)].value
        if sg_name not in sg_names:
            sg_names.append(sg_name)
        if sg_description not in sg_descriptions:
            sg_descriptions.append(sg_description)

# Create the SGs:
print("Implementing SGs based on local dir SNB 'Sheet1'...")
for i, o in zip(sg_names,sg_descriptions):
    sg = conn.create_security_group(GroupName=i,Description=o,VpcId=vpc_id)
    time.sleep(2)
    sg_lib[i] = sg['GroupId']
    conn.create_tags(Resources=[sg['GroupId']],Tags=[{'Key': 'Name', 'Value': i}])

# Creat Infrastructure Management SG:
# Get CIDR from VPC id:
vpc_info = conn.describe_vpcs(VpcIds=[vpc_id])
cidr_blk = vpc_info['Vpcs'][0]['CidrBlock']
try:
    infra_sg = conn.create_security_group(GroupName='Infrastructure-Management-SG',Description='Cloud Operations - Remote Access, AD Services, etc',VpcId=vpc_id)
    conn.create_tags(Resources=[infra_sg['GroupId']],Tags=[{'Key': 'Name', 'Value': 'Infrastructure-Management-SG'}])
    conn.authorize_security_group_ingress(GroupId=infra_sg['GroupId'],IpProtocol='tcp',FromPort=22,ToPort=22,CidrIp=cidr_blk)
    conn.authorize_security_group_ingress(GroupId=infra_sg['GroupId'],IpProtocol='tcp',FromPort=22,ToPort=22,CidrIp='172.25.10.140/32')
    conn.authorize_security_group_ingress(GroupId=infra_sg['GroupId'],IpProtocol='tcp',FromPort=22,ToPort=22,CidrIp='172.25.17.22/32')
except:
    pass

print('SGs Created!')

#####################
# Implement SG Rules:
#####################
print('Implementing Rules...')    
# Implement SG Rules:
for i in sg_lib.keys():
    for x in range(4,500):
        if sgr['C{}'.format(x)].value == None:
            continue
        else:
            sg_id = sg_lib[i]
            all_protocols = '-1'
            if sgr['F{}'.format(x)].value == 'All':
                protocol = 'All'
            else:
                protocol = sgr['F{}'.format(x)].value.lower()
            if sgr['G{}'.format(x)].value == 'All':
                port = 'All'
            elif type(sgr['G{}'.format(x)].value) == long:
                port = str(sgr['G{}'.format(x)].value)
            # Account for ranges:
            elif ' - ' in str(sgr['G{}'.format(x)].value):
                port = str(sgr['G{}'.format(x)].value)
                port = port.split(' - ')
                from_port = int(port[0])
                to_port = int(port[1])
            elif '-' in str(sgr['G{}'.format(x)].value):
                port = str(sgr['G{}'.format(x)].value)
                port = port.split('-')
                from_port = int(port[0])
                to_port = int(port[1])
            else:
                port = str(sgr['G{}'.format(x)].value)
            if sgr['I{}'.format(x)].value in sg_lib.keys():
                allowed_source = sg_lib[sgr['I{}'.format(x)].value]
            else:
                allowed_source = sgr['I{}'.format(x)].value
                allowed_source = allowed_source.replace('\n', '')
            sg_name = sgr['C{}'.format(x)].value
            direction = sgr['D{}'.format(x)].value

            if i == sg_name and direction == 'Inbound':

                if sg_name in sgr['I{}'.format(x)].value and protocol == 'All':
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpPermissions=[{'IpProtocol':'-1','UserIdGroupPairs':[{'GroupId':allowed_source,'VpcId':vpc_id}]}])
                    except:
                        pass

                elif allowed_source in sg_lib.keys() and protocol == 'All':
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpPermissions=[{'IpProtocol':'-1','UserIdGroupPairs':[{'GroupId':allowed_source,'VpcId':vpc_id}]}])
                    except:
                        pass
                
                elif protocol == 'All' and port == 'All':
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=all_protocols,CidrIp=allowed_source)
                    except:
                        pass

                elif sgr['I{}'.format(x)].value in sg_lib.keys() and '-' in str(sgr['G{}'.format(x)].value):
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpPermissions=[{'IpProtocol':protocol,'FromPort':from_port,'ToPort':to_port,'UserIdGroupPairs':[{'GroupId':allowed_source,'VpcId':vpc_id}]}])
                    except:
                        pass

                elif sgr['I{}'.format(x)].value in sg_lib.keys() and ',' in str(sgr['G{}'.format(x)].value):
                    port = str(sgr['G{}'.format(x)].value)
                    port = port.replace(' ', '')
                    port = port.split(',')
                    for y in port:
                        try:
                            conn.authorize_security_group_ingress(GroupId=sg_id,IpPermissions=[{'IpProtocol':protocol,'FromPort':int(y),'ToPort':int(y),'UserIdGroupPairs':[{'GroupId':allowed_source,'VpcId':vpc_id}]}])
                        except:
                            pass

                elif sgr['I{}'.format(x)].value in sg_lib.keys():
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpPermissions=[{'IpProtocol':protocol,'FromPort':int(port),'ToPort':int(port),'UserIdGroupPairs':[{'GroupId':allowed_source,'VpcId':vpc_id}]}])
                    except:
                        pass

                elif ',' in str(sgr['G{}'.format(x)].value) and 'Hosted VPC' in sgr['I{}'.format(x)].value:
                    port = str(sgr['G{}'.format(x)].value)
                    port = port.replace(' ', '')
                    port = port.split(',')
                    for y in port:
                        try:
                            conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=int(y),ToPort=int(y),CidrIp=cidr_blk)
                        except:
                            pass

                elif ',' in str(sgr['G{}'.format(x)].value):
                    port = str(sgr['G{}'.format(x)].value)
                    port = port.replace(' ', '')
                    port = port.split(',')
                    for y in port:
                        try:
                            conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=int(y),ToPort=int(y),CidrIp=allowed_source)
                        except:
                            pass

                elif ' - ' in str(sgr['G{}'.format(x)].value) and 'Hosted VPC' in sgr['I{}'.format(x)].value:
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=from_port,ToPort=to_port,CidrIp=cidr_blk)
                    except:
                        pass

                elif '-' in str(sgr['G{}'.format(x)].value) and 'Hosted VPC' in sgr['I{}'.format(x)].value:
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=from_port,ToPort=to_port,CidrIp=cidr_blk)
                    except:
                        pass


                elif 'Hosted VPC' in sgr['I{}'.format(x)].value:
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=int(port),ToPort=int(port),CidrIp=cidr_blk)
                    except:
                        pass


                elif ' - ' in str(sgr['G{}'.format(x)].value):
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=from_port,ToPort=to_port,CidrIp=allowed_source)
                    except:
                        pass

                elif '-' in str(sgr['G{}'.format(x)].value):
                    try:
                        conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=from_port,ToPort=to_port,CidrIp=allowed_source)
                    except:
                        pass

                elif sgr['I{}'.format(x)].value not in sg_lib.keys():
                    if port == 'All':
                        try:
                            conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=0,ToPort=65535,CidrIp=allowed_source)
                        except:
                            pass
                    else:
                        try:
                            conn.authorize_security_group_ingress(GroupId=sg_id,IpProtocol=protocol,FromPort=int(port),ToPort=int(port),CidrIp=allowed_source)
                        except:
                            pass

            elif i == sg_name and direction == 'Outbound':
                
                if protocol == 'All' and port == 'All':
                    try:
                        conn.authorize_security_group_egress(GroupId=sg_id,IpProtocol=all_protocols,CidrIp=allowed_source)
                    except:
                        pass

                elif port == 'All':
                        try:
                            conn.authorize_security_group_egress(GroupId=sg_id,IpProtocol=protocol,FromPort=0,ToPort=65535,CidrIp=allowed_source)
                        except:
                            pass
                else:
                    try:
                        conn.authorize_security_group_egress(GroupId=sg_id,IpProtocol=protocol,FromPort=port,ToPort=port,CidrIp=allowed_source)
                    except:
                        pass

                
print('Rules Implemented!')
print('Execution Complete!')



