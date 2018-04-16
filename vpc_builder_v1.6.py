############################################################
#  AWS VPC Builder v1.6                                    #
#  Author: Bobby Williams                                  #
#  Contact: bobby.williams@xxxxxxxx.com                    #
############################################################

import openpyxl, boto3, os, re, time, getpass, sys, warnings 
import subprocess as sp


# Ask for the client's shortname:
print("What's the client's short name? (ex. DUKE, UOP, MAYOC, etc.)")
shortname = raw_input('> ')
shortname = shortname.upper()
# SNB check:
print("Do you have the client's SNB in same directory as this script? (y/n)")
snb_in_dir = raw_input('> ')
while snb_in_dir not in 'yYnN':
    print('Invalid selection!')
    print("Do you have the client's SNB in same directory as this script? (y/n)")
    snb_in_dir = raw_input('> ')
if snb_in_dir in 'nN':
    print('Sorry, but SNB is required in same directory as this script before continuing')
    print('Exiting...')
    sys.exit()
# Ask if Prod or DR:
print("Is this Prod or DR? (a = Prod, b = DR)")
build_type = raw_input('> ')
while build_type not in 'aAbB':
    print("Invalid selection!")
    print("Is this DR or Prod? (a = Prod, b = DR)")
    build_type = raw_input('> ')
if build_type in 'aA':
    build_type = 'Prod'
    vpc_name = 'banner-Prod-{}-vpc'.format(shortname)
    # Get the client's assigned CIDR:
    print("What's the client's assigned CIDR block? (ex. 10.120.18.0/23)")
    cidr_blk = raw_input('> ') # VPC CIDR  
else:
    build_type = 'DR'
    vpc_name = 'banner-DR-{}-vpc'.format(shortname)
    # Check to see if CE-ISO DR needed:
    print('Create CE-ISO VPC? (y/n)')
    ce_iso_vpc = raw_input('> ')
    while ce_iso_vpc not in 'yYnN':
        print('Invalid response!')
        print('Create CE-ISO VPC? (y/n)')
        ce_iso_vpc = raw_input('> ')
    if ce_iso_vpc in 'yY':
        # Get the client's CE-ISO CIDR:
        print("What's client's CE-ISO CIDR block? (ex. 172.27.22.0/24)")
        ce_iso_cidr = raw_input('> ')
        # Get the client's assigned CIDR:
        print("What's the client's assigned CIDR block? (ex. 10.120.18.0/23)")
        cidr_blk = raw_input('> ') # VPC CIDR
    else:
        # Get the client's assigned CIDR:
        print("What's the client's assigned CIDR block? (ex. 10.120.18.0/23)")
        cidr_blk = raw_input('> ') # VPC CIDR
        
# Get region for build-out:
print("Choose your Region (pick a letter):")
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
    print("Choose your Region (pick a letter):")
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
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'bB':
    region = 'us-east-2'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'cC':
    region = 'us-west-1'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'dD':
    region = 'us-west-2'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'eE':
    region = 'ca-central-1'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'fF':
    region = 'eu-west-1'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'gG':
    region = 'eu-central-1'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'hH':
    region = 'eu-west-2'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'iI':
    region = 'ap-northeast-1'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'jJ':
    region = 'ap-northeast-2'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'kK':
    region = 'ap-southeast-1'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'lL':
    region = 'ap-southeast-2'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'mM':
    region = 'ap-south-1'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']
elif get_region in 'nN':
    region = 'sa-east-1'
    dns_srv = ['172.25.16.40', '172.25.16.140']
    ntp_srv = ['172.25.17.15', '172.25.17.146']

public_dev_subnet = cidr_blk.replace(cidr_blk[-3:], '')+'/25' # Public DEV/NON-PROD Subnet

chop1 = cidr_blk.replace(cidr_blk[-3:], '')
chop1 = chop1.split('.')
chop1[3] = '128'

public_prod_subnet = '.'.join(chop1)+'/25' # Public Prod Subnet

chop = cidr_blk.replace(cidr_blk[-3:], '')
chop = chop.split('.')
chop[2] = str(int(chop[2])+1)

priv_dev_subnet = '.'.join(chop)+'/25' # Private DEV/NON-PROD Subnet

chop2 = cidr_blk.replace(cidr_blk[-3:], '')
chop2 = chop2.split('.')
chop2[2] = str(int(chop2[2])+1)
chop2[3] = '128'

priv_prod_subnet = '.'.join(chop2)+'/25' # Private PROD Subnet

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

##############
# Create VPC:
##############
print('Creating VPC...')
vpc = conn.create_vpc(CidrBlock=cidr_blk)
vpc_id = vpc['Vpc']['VpcId']
time.sleep(2)
# Check to see if VPC exists:
vpc_exists = conn.get_waiter('vpc_exists')
vpc_exists.wait(VpcIds=[vpc_id])

# Check to see if VPC available:
check_vpc = conn.get_waiter('vpc_available')
check_vpc.wait(VpcIds=[vpc_id])

# Name the VPC:
conn.create_tags(Resources=[vpc_id],Tags=[{'Key': 'Name', 'Value': vpc_name}])
print('VPC created!')

##################
# Create Subnets:
##################
print('Creating Subnets...')
create_public_dev_subnet = conn.create_subnet(VpcId=vpc_id,CidrBlock=public_dev_subnet,AvailabilityZone=region+'a')
public_dev_subnet_id = create_public_dev_subnet['Subnet']['SubnetId']
public_dev_subnet_name = 'banner-{}-{}-public_subnet-0'.format(shortname,build_type)

create_public_prod_subnet = conn.create_subnet(VpcId=vpc_id,CidrBlock=public_prod_subnet,AvailabilityZone=region+'b')
public_prod_subnet_id = create_public_prod_subnet['Subnet']['SubnetId']
public_prod_subnet_name = 'banner-{}-{}-public_subnet-1'.format(shortname,build_type)

create_priv_dev_subnet = conn.create_subnet(VpcId=vpc_id,CidrBlock=priv_dev_subnet,AvailabilityZone=region+'a')
priv_dev_subnet_id = create_priv_dev_subnet['Subnet']['SubnetId']
priv_dev_subnet_name = 'banner-{}-{}-private_subnet-0'.format(shortname,build_type)

create_priv_prod_subnet = conn.create_subnet(VpcId=vpc_id,CidrBlock=priv_prod_subnet,AvailabilityZone=region+'b')
priv_prod_subnet_id = create_priv_prod_subnet['Subnet']['SubnetId']
priv_prod_subnet_name = 'banner-{}-{}-private_subnet-1'.format(shortname,build_type)

time.sleep(2)
# Check to see if subnets are ready/available:
check_subnets = conn.get_waiter('subnet_available')
check_subnets.wait(SubnetIds=[public_dev_subnet_id,public_prod_subnet_id,priv_dev_subnet_id,priv_prod_subnet_id])

conn.create_tags(Resources=[public_dev_subnet_id],Tags=[{'Key': 'Name', 'Value': public_dev_subnet_name}])
conn.create_tags(Resources=[public_prod_subnet_id],Tags=[{'Key': 'Name', 'Value': public_prod_subnet_name}])
conn.create_tags(Resources=[priv_dev_subnet_id],Tags=[{'Key': 'Name', 'Value': priv_dev_subnet_name}])
conn.create_tags(Resources=[priv_prod_subnet_id],Tags=[{'Key': 'Name', 'Value': priv_prod_subnet_name}])
print('Subnets Created!')

######################
# Create Route Tables:
######################
print('Creating Route Tables...')
create_public_dev_rt = conn.create_route_table(VpcId=vpc_id)
public_dev_rt_id = create_public_dev_rt['RouteTable']['RouteTableId']
public_dev_rt_name = 'banner-{}-pub_rt-0'.format(shortname)
conn.associate_route_table(SubnetId=public_dev_subnet_id,RouteTableId=public_dev_rt_id)

create_public_prod_rt = conn.create_route_table(VpcId=vpc_id)
public_prod_rt_id = create_public_prod_rt['RouteTable']['RouteTableId']
public_prod_rt_name = 'banner-{}-pub_rt-1'.format(shortname)
conn.associate_route_table(SubnetId=public_prod_subnet_id,RouteTableId=public_prod_rt_id)

create_priv_dev_rt = conn.create_route_table(VpcId=vpc_id)
priv_dev_rt_id = create_priv_dev_rt['RouteTable']['RouteTableId']
priv_dev_rt_name = 'banner-{}-priv_rt-0'.format(shortname)
conn.associate_route_table(SubnetId=priv_dev_subnet_id,RouteTableId=priv_dev_rt_id)

create_priv_prod_rt = conn.create_route_table(VpcId=vpc_id)
priv_prod_rt_id = create_priv_prod_rt['RouteTable']['RouteTableId']
priv_prod_rt_name = 'banner-{}-priv_rt-1'.format(shortname)
conn.associate_route_table(SubnetId=priv_prod_subnet_id,RouteTableId=priv_prod_rt_id)

conn.create_tags(Resources=[public_dev_rt_id],Tags=[{'Key': 'Name', 'Value': public_dev_rt_name}])
conn.create_tags(Resources=[public_prod_rt_id],Tags=[{'Key': 'Name', 'Value': public_prod_rt_name}])
conn.create_tags(Resources=[priv_dev_rt_id],Tags=[{'Key': 'Name', 'Value': priv_dev_rt_name}])
conn.create_tags(Resources=[priv_prod_rt_id],Tags=[{'Key': 'Name', 'Value': priv_prod_rt_name}])

time.sleep(3)
print('Route Tables Created!')

route_tables = [public_dev_rt_id,public_prod_rt_id,priv_dev_rt_id,priv_prod_rt_id]

#####################################
# Create and Attach Internet Gateway:
#####################################
print('Creating Internet Gateway...')
create_internet_gateway = conn.create_internet_gateway()
internet_gateway_id = create_internet_gateway['InternetGateway']['InternetGatewayId']
internet_gateway_name = 'banner-{}-{}-internet_gateway'.format(build_type,shortname)
time.sleep(3)
conn.create_tags(Resources=[internet_gateway_id],Tags=[{'Key': 'Name', 'Value': internet_gateway_name}])
print('Internet Gateway Created!')
print('Attaching Internet Gateway to VPC...')
attach_internet_gateway = conn.attach_internet_gateway(InternetGatewayId=internet_gateway_id,VpcId=vpc_id)
time.sleep(3)
print('Internet Gateway attached to VPC!')

############################################
# Create and Attach Virtual Private Gateway:
############################################
print('Creating Virtual Private Gateway...')
create_vpn_gateway = conn.create_vpn_gateway(Type='ipsec.1')
vpn_gateway_id = create_vpn_gateway['VpnGateway']['VpnGatewayId']
vpn_gateway_name = '{}-{}-vpc-vgw'.format(shortname,build_type)
time.sleep(3)
print('Virtual Private Gateway Created!')
print('Attaching Virtual Private Gateway to VPC...')
attach_vpn_gateway = conn.attach_vpn_gateway(VpnGatewayId=vpn_gateway_id,VpcId=vpc_id)
time.sleep(3)
conn.create_tags(Resources=[vpn_gateway_id],Tags=[{'Key': 'Name', 'Value': vpn_gateway_name}])
print('Virtual Private Gateway attached to VPC!')
time.sleep(6)
for i in route_tables:
    conn.enable_vgw_route_propagation(RouteTableId=i,GatewayId=vpn_gateway_id)

################################
# Allocate EIPs for Nat Gatways:
################################
print('Allocating EIPs for Nat Gateways')
eips = []
for i in range(2):
    eip = conn.allocate_address(Domain='vpc')
    time.sleep(3)
    if eip['AllocationId'] not in eips:
        eips.append(eip['AllocationId'])
print('EIPs Allocated!')

######################
# Create NAT Gateways:
######################
print('Creating NAT Gateways...')
nat_gateway1 = conn.create_nat_gateway(SubnetId=public_dev_subnet_id,AllocationId=eips[0])
nat_gateway1_id = nat_gateway1['NatGateway']['NatGatewayId']
time.sleep(3)
nat_gateway2 = conn.create_nat_gateway(SubnetId=public_prod_subnet_id,AllocationId=eips[1])
nat_gateway2_id = nat_gateway2['NatGateway']['NatGatewayId']
print('NAT Gateways Created!')

###################
# Set DHCP Options:
###################
print('Setting DHCP Options...')
set_dhcp_options = conn.create_dhcp_options(DhcpConfigurations=[
    {
        'Key': 'domain-name',
        'Values': ['ad.admin XXXXXXXX.com']
        },
    {
        'Key': 'domain-name-servers',
        'Values': [dns_srv[0],dns_srv[1]]
        },
    {
        'Key':'ntp-servers',
        'Values': [ntp_srv[0],ntp_srv[1]]
        }
    ]

)
dhcp_options_id = set_dhcp_options['DhcpOptions']['DhcpOptionsId']
dhcp_options_name = 'banner-{}-{}-dhcp-options'.format(shortname,build_type)
conn.associate_dhcp_options(DhcpOptionsId=dhcp_options_id,VpcId=vpc_id)
conn.create_tags(Resources=[dhcp_options_id],Tags=[{'Key': 'Name', 'Value': dhcp_options_name}])
time.sleep(3)
print('DHCP Options Set!')

#####################################
# Add Default Routes to route tables:
#####################################
print('Adding default routes to route tables...')
try:
    conn.create_route(RouteTableId=public_dev_rt_id,DestinationCidrBlock='0.0.0.0/0',GatewayId=internet_gateway_id)
    time.sleep(2)
    conn.create_route(RouteTableId=public_prod_rt_id,DestinationCidrBlock='0.0.0.0/0',GatewayId=internet_gateway_id)
    time.sleep(2)
    conn.create_route(RouteTableId=priv_dev_rt_id,DestinationCidrBlock='0.0.0.0/0',GatewayId=nat_gateway1_id)
    time.sleep(2)
    conn.create_route(RouteTableId=priv_prod_rt_id,DestinationCidrBlock='0.0.0.0/0',GatewayId=nat_gateway2_id)
    time.sleep(2)
    print('Default routes added!')
except:
    pass
    

if build_type == 'DR':
    if ce_iso_vpc in 'yY':
        ####################
        # Create CE-ISO VPC:
        ####################
        print('Creating CE-ISO VPC...')
        ce_vpc_name = 'CE-{}-ISO-DR'.format(shortname)
        ce_vpc = conn.create_vpc(CidrBlock=ce_iso_cidr)
        ce_vpc_id = ce_vpc['Vpc']['VpcId']
        time.sleep(2)
        # Check to see if VPC exists:
        vpc_exists = conn.get_waiter('vpc_exists')
        vpc_exists.wait(VpcIds=[ce_vpc_id])

        # Check to see if VPC available:
        check_vpc = conn.get_waiter('vpc_available')
        check_vpc.wait(VpcIds=[ce_vpc_id])

        # Name the VPC:
        conn.create_tags(Resources=[ce_vpc_id],Tags=[{'Key': 'Name', 'Value': ce_vpc_name}])
        print('CE-ISO VPC created!')

        ce_iso_subnet = ce_iso_cidr

        ################
        # Create Subnet:
        ################
        print('Creating CE-ISO Subnet...')
        create_ce_subnet = conn.create_subnet(VpcId=ce_vpc_id,CidrBlock=ce_iso_cidr,AvailabilityZone=region+'a')
        ce_subnet_id = create_ce_subnet['Subnet']['SubnetId']
        ce_subnet_name = 'CE-{}-ISO-{}'.format(shortname,build_type)
        # Check to see if subnets are ready/available:
        check_subnets = conn.get_waiter('subnet_available')
        check_subnets.wait(SubnetIds=[ce_subnet_id])
        conn.create_tags(Resources=[ce_subnet_id],Tags=[{'Key': 'Name', 'Value': ce_subnet_name}])
        #####################
        # Create Route Table:
        #####################
        print('Creating CE-ISO Route Table...')
        create_ce_rt = conn.create_route_table(VpcId=ce_vpc_id)
        ce_rt_id = create_ce_rt['RouteTable']['RouteTableId']
        ce_rt_name = 'CE-RTB'
        time.sleep(2)
        conn.associate_route_table(SubnetId=ce_subnet_id,RouteTableId=ce_rt_id)
        conn.create_tags(Resources=[ce_rt_id],Tags=[{'Key': 'Name', 'Value': ce_rt_name}])
        
        #####################################
        # Create and Attach Internet Gateway:
        #####################################
        print('Creating CE-ISO Internet Gateway...')
        create_ce_internet_gateway = conn.create_internet_gateway()
        ce_internet_gateway_id = create_ce_internet_gateway['InternetGateway']['InternetGatewayId']
        ce_internet_gateway_name = 'CE-IGW'
        time.sleep(3)
        conn.create_tags(Resources=[ce_internet_gateway_id],Tags=[{'Key': 'Name', 'Value': ce_internet_gateway_name}])
        print('CE-ISO Internet Gateway Created!')
        print('Attaching CE-ISO Internet Gateway to VPC...')
        attach_internet_gateway = conn.attach_internet_gateway(InternetGatewayId=ce_internet_gateway_id,VpcId=ce_vpc_id)
        time.sleep(3)
        print('CE-ISO Internet Gateway attached to VPC!')

        ############################################
        # Create and Attach Virtual Private Gateway:
        ############################################
        print('Creating CE-ISO Virtual Private Gateway...')
        create_ce_vpn_gateway = conn.create_vpn_gateway(Type='ipsec.1')
        ce_vpn_gateway_id = create_ce_vpn_gateway['VpnGateway']['VpnGatewayId']
        ce_vpn_gateway_name = '{}-CE-VPC-VGW'.format(shortname)
        time.sleep(3)
        print('CE-ISO Virtual Private Gateway Created!')
        print('Attaching CE-ISO Virtual Private Gateway to VPC...')
        ce_attach_vpn_gateway = conn.attach_vpn_gateway(VpnGatewayId=ce_vpn_gateway_id,VpcId=ce_vpc_id)
        time.sleep(3)
        conn.create_tags(Resources=[ce_vpn_gateway_id],Tags=[{'Key': 'Name', 'Value': ce_vpn_gateway_name}])
        print('CE-ISO Virtual Private Gateway attached to VPC!')
        time.sleep(6)
        conn.enable_vgw_route_propagation(RouteTableId=ce_rt_id,GatewayId=ce_vpn_gateway_id)

        #####################################
        # Add Default Routes to route tables:
        #####################################
        print('Adding default route to route table...')
        try:
            conn.create_route(RouteTableId=ce_rt_id,DestinationCidrBlock='0.0.0.0/0',GatewayId=ce_internet_gateway_id)
            print('Default route added!')
        except:
            pass
        print('Execution Complete!')

    else:
        print('Execution Complete!')
else:
    ####################################
    # Generate ENIs, IPs + Populate SNB:
    ####################################
    # Open the SNB in local directory and load ERP-SNB worksheet:
    print('Opening SNB in local dir...')
    warnings.filterwarnings('ignore') # Ignore openpyxl UserWarning
    wb = openpyxl.load_workbook('{} XXXX CS Server Network Build-AWS.xlsx'.format(shortname))
    ###############
    # Populate ToC:
    ###############
    print("Populating 'Table of Contents' sheet with VPC info...")
    try:
        tob = wb.get_sheet_by_name('Table of Contents')
        time.sleep(3)
        tob['B17'].value = vpc_id
        tob['B18'].value = cidr_blk
        tob['B19'].value = public_dev_subnet
        tob['B20'].value = public_prod_subnet
        tob['B21'].value = priv_dev_subnet
        tob['B22'].value = priv_prod_subnet
    except:
        pass
    ###############################
    snb = wb.get_sheet_by_name('ERP-SNB')
    time.sleep(3)
    print('Generating ENIs + populating SNB...')
    if 'DNS' in snb['G1'].value:
        for i in range(2,100):
            if snb['D{}'.format(i)].value == None:
                continue
            elif snb['D{}'.format(i)].value == 'NON-PROD' and snb['E{}'.format(i)].value == 'Private':
                eni = conn.create_network_interface(SubnetId=priv_dev_subnet_id,Description=snb['C{}'.format(i)].value)
                snb['I{}'.format(i)].value = eni['NetworkInterface']['NetworkInterfaceId']
                snb['H{}'.format(i)].value = eni['NetworkInterface']['PrivateIpAddress']
                
            elif snb['D{}'.format(i)].value == 'NON-PROD' and snb['E{}'.format(i)].value == 'Public':
                eni = conn.create_network_interface(SubnetId=public_dev_subnet_id,Description=snb['C{}'.format(i)].value)
                snb['I{}'.format(i)].value = eni['NetworkInterface']['NetworkInterfaceId']
                snb['H{}'.format(i)].value = eni['NetworkInterface']['PrivateIpAddress']
                
            elif snb['D{}'.format(i)].value == 'PROD' and snb['E{}'.format(i)].value == 'Private':
                eni = conn.create_network_interface(SubnetId=priv_prod_subnet_id,Description=snb['C{}'.format(i)].value)
                snb['I{}'.format(i)].value = eni['NetworkInterface']['NetworkInterfaceId']
                snb['H{}'.format(i)].value = eni['NetworkInterface']['PrivateIpAddress']

            elif snb['D{}'.format(i)].value == 'PROD' and snb['E{}'.format(i)].value == 'Public':
                eni = conn.create_network_interface(SubnetId=public_prod_subnet_id,Description=snb['C{}'.format(i)].value)
                snb['I{}'.format(i)].value = eni['NetworkInterface']['NetworkInterfaceId']
                snb['H{}'.format(i)].value = eni['NetworkInterface']['PrivateIpAddress']
    else:
        
        for i in range(2,100):
            if snb['D{}'.format(i)].value == None:
                continue
            elif snb['D{}'.format(i)].value == 'NON-PROD' and snb['E{}'.format(i)].value == 'Private':
                eni = conn.create_network_interface(SubnetId=priv_dev_subnet_id,Description=snb['C{}'.format(i)].value)
                snb['H{}'.format(i)].value = eni['NetworkInterface']['NetworkInterfaceId']
                snb['G{}'.format(i)].value = eni['NetworkInterface']['PrivateIpAddress']
                
            elif snb['D{}'.format(i)].value == 'NON-PROD' and snb['E{}'.format(i)].value == 'Public':
                eni = conn.create_network_interface(SubnetId=public_dev_subnet_id,Description=snb['C{}'.format(i)].value)
                snb['H{}'.format(i)].value = eni['NetworkInterface']['NetworkInterfaceId']
                snb['G{}'.format(i)].value = eni['NetworkInterface']['PrivateIpAddress']
                
            elif snb['D{}'.format(i)].value == 'PROD' and snb['E{}'.format(i)].value == 'Private':
                eni = conn.create_network_interface(SubnetId=priv_prod_subnet_id,Description=snb['C{}'.format(i)].value)
                snb['H{}'.format(i)].value = eni['NetworkInterface']['NetworkInterfaceId']
                snb['G{}'.format(i)].value = eni['NetworkInterface']['PrivateIpAddress']

            elif snb['D{}'.format(i)].value == 'PROD' and snb['E{}'.format(i)].value == 'Public':
                eni = conn.create_network_interface(SubnetId=public_prod_subnet_id,Description=snb['C{}'.format(i)].value)
                snb['H{}'.format(i)].value = eni['NetworkInterface']['NetworkInterfaceId']
                snb['G{}'.format(i)].value = eni['NetworkInterface']['PrivateIpAddress']

    time.sleep(3)
    print('SNB populated, saving results...'.format(shortname))
    wb.save('{} XXXX CS Server Network Build-AWS.xlsx'.format(shortname))
    print('Execution Complete!')


