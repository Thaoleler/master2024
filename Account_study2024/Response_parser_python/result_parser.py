ID_INDEX = 0
DEVICES_INDEX = 1

GOOGLE_INDEX = 13
APPLE_INDEX = 13
FACEBOOK_INDEX = 13

GITHUB_INDEX = 13
LINKEDIN_INDEX = 13

DEVICES = ["p1", "p2", "p3", "c1", "c2", "c3", "t1", "t2","sw1", "sw2", "s1", "s2"]

def parse_number(val):
    if val == "None":
        return 0
    elif val == "4 or more":
        return 4
    else:
        return int(val)

def parse_index(row):
    return row[ID_INDEX]

def parse_devices(row):
    devices = []
    num_phone = 0
    num_computer = 0
    num_tablet = 0
    num_smart_watch = 0
    num_security_key = 0

    #Why are these here??
    devices.append({"id": "mem1", "label": "Memory"})
    devices.append({"id": "pap1", "label": "Paper"})

    for i in range(12):
        if not row[DEVICES_INDEX+i] == "":
            device_label = ""
            if row[DEVICES_INDEX+i][0] == "p":
                num_phone += 1
                device_label = "Phone {}".format(num_phone)
            elif row[DEVICES_INDEX+i][0] == "c":
                num_computer += 1
                device_label = "Computer {}".format(num_computer)
            elif row[DEVICES_INDEX+i][0] == "t":
                num_tablet += 1
                device_label = "Tablet {}".format(num_tablet)
            elif row[DEVICES_INDEX+i][0:2] == "sw":
                num_smart_watch += 1
                device_label = "SmartWatch {}".format(num_smart_watch)
            elif row[DEVICES_INDEX+i][0] == "s":
                num_security_key += 1
                device_label = "SecKey {}".format(num_security_key)
            devices.append(
                {"id": row[DEVICES_INDEX+i], "label": device_label})

    return devices


def parse_device_selection(row, start_index, num):
    devices = []
    for i in range(num):
        if not row[start_index+i] == "":
            devices.append(row[start_index+i])
    return devices


def parse_password_access(row, start_index):
    MEMORY_INDEX = start_index
    PASSWORD_MANAGER_INDEX = start_index+1
    DEVICE_STORE_INDEX = start_index+2
    PAPER_INDEX = start_index+3
    PASSWORD_MANAGER_DEVICES_INDEX = start_index+4
    DEVICE_STORE_DEVICES_INDEX = start_index+12

    password_access = {"nodeId": "password", "devices": []}
    if not row[MEMORY_INDEX] == "":
        password_access["devices"].append("mem1")
    if not row[PAPER_INDEX] == "":
        password_access["devices"].append("pap1")

    if not row[PASSWORD_MANAGER_INDEX] == "":
        password_access["devices"] += parse_device_selection(
            row, PASSWORD_MANAGER_DEVICES_INDEX, 8)
    if not row[DEVICE_STORE_INDEX] == "":
        password_access["devices"] += parse_device_selection(
            row, DEVICE_STORE_DEVICES_INDEX, 8)
    password_access["devices"] = list(dict.fromkeys(password_access["devices"]))
    return password_access


def parse_Google_account(row):
    deviceList = parse_devices(row)

    auth_nodes = []
    second_factor = False
    passkeys = False

    PASSWORD_ACCESS_INDEX = GOOGLE_INDEX+1
    SECOND_FACTOR_ENABLED_INDEX = GOOGLE_INDEX+21 #34
    PASSKEYS_ENABLED_INDEX = GOOGLE_INDEX+22 #35
    PASSKEYS_ENABLED_DEVICES_INDEX = GOOGLE_INDEX+23 #36-43
    #SIGN_IN_BY_PHONE_ENABLED = GOOGLE_INDEX+22
    #SIGN_IN_BY_PHONE_DEVICES_INDEX = GOOGLE_INDEX+23  # 5
    SECOND_FACTOR_METHODS_INDEX = GOOGLE_INDEX+31 #44

    GOOGLE_PROMPTS_DEVICES_INDEX = GOOGLE_INDEX+36  #49
    AUTHENTICATOR_APP_DEVICES_INDEX = GOOGLE_INDEX+41  #54
    PHONE_DEVICES_INDEX = GOOGLE_INDEX+49  #62
    SECURITY_KEY_DEVICES_INDEX = GOOGLE_INDEX+52  #65

    RECOVERY_METHODS_INDEX = GOOGLE_INDEX+62 #75
    RECOVERY_PHONE_DEVICES_INDEX = GOOGLE_INDEX+64 #77

    # Password access
    auth_nodes.append(parse_password_access(row, PASSWORD_ACCESS_INDEX))

    # Second factor
    if row[SECOND_FACTOR_ENABLED_INDEX] == "yes":
        second_factor = True

    # Passkeys
    if row[PASSKEYS_ENABLED_INDEX] == "yes":
        passkeys = True

        if not row[PASSKEYS_ENABLED_DEVICES_INDEX] == "":
            devices = []
            print("passkeys??")
            devices = parse_device_selection(
                row, PASSKEYS_ENABLED_DEVICES_INDEX, 8)
            auth_nodes.append({"nodeId": "Passkeys", "devices": devices})
            print(devices)

    if second_factor:
        for i in range(5):
            if not row[SECOND_FACTOR_METHODS_INDEX+i] == "":
                # parse devices
                devices = []
                if i == 0:
                    devices = parse_device_selection(
                        row, GOOGLE_PROMPTS_DEVICES_INDEX, 5)
                elif i == 1:
                    devices = parse_device_selection(
                        row, AUTHENTICATOR_APP_DEVICES_INDEX, 8)
                elif i == 2:
                    devices = parse_device_selection(
                        row, PHONE_DEVICES_INDEX, 3)
                elif i == 4:
                    devices = parse_device_selection(
                        row, SECURITY_KEY_DEVICES_INDEX, 10)
                auth_nodes.append(
                    {"nodeId": row[SECOND_FACTOR_METHODS_INDEX+i], "devices": devices})

    # Recovery
    for i in range(2):
        if not row[RECOVERY_METHODS_INDEX+i] == "":
            devices = []
            if i == 0:
                devices = parse_device_selection(
                    row, RECOVERY_PHONE_DEVICES_INDEX, 3)

            auth_nodes.append(
                {"nodeId": row[RECOVERY_METHODS_INDEX+i], "devices": devices})

    #print({"auth_nodes": auth_nodes, "devices": deviceList})
    return {"auth_nodes": auth_nodes, "devices": deviceList}


def parse_Apple_account(row):
    deviceList = parse_devices(row)
    auth_nodes = []
    #secondary_methods = []
    #fallback_methods = []

    PASSWORD_ACCESS_INDEX = APPLE_INDEX+1
    TRUSTED_PHONE_NUMBERS_INDEX = APPLE_INDEX+21
    TRUSTED_DEVICES_INDEX = APPLE_INDEX+25
    SECURITY_KEYS_INDEX = APPLE_INDEX+36
    RECOVERY_METHODS_INDEX = APPLE_INDEX+39
    RECOVERY_KEYS_DEVICES_INDEX = APPLE_INDEX+42

    auth_nodes.append(parse_password_access(row, PASSWORD_ACCESS_INDEX))

    trusted_devices = parse_device_selection(
        row, TRUSTED_DEVICES_INDEX, 10)
    if len(trusted_devices) > 0:
        auth_nodes.append({"nodeId": "trusted_device", "devices": trusted_devices})

    trusted_phones = parse_device_selection(
        row, TRUSTED_PHONE_NUMBERS_INDEX, 3)
    if len(trusted_phones) > 0:
         auth_nodes.append({"nodeId": "trusted_phone", "devices": trusted_phones})

    security_key = parse_device_selection(
        row, SECURITY_KEYS_INDEX, 2)
    if len(security_key) > 0:
        auth_nodes.append({"nodeId": "security_key", "devices": security_key})

    recovery_keys = parse_device_selection(
        row, RECOVERY_KEYS_DEVICES_INDEX, 2)
    if not row[RECOVERY_METHODS_INDEX+1] == "":
        auth_nodes.append({"nodeId": "fallback_recovery_key", "devices": recovery_keys})
        #deviceList.append({"id":"pap2", "label": "Paper"})
    elif len(trusted_devices) > 0:
        auth_nodes.append({"nodeId": "fallback_device", "devices": trusted_devices})

    return {"auth_nodes": auth_nodes, "devices": deviceList}

def parse_Facebook_account(row):
    deviceList = parse_devices(row)

    auth_nodes = []
    second_factor = False

    PASSWORD_ACCESS_INDEX = FACEBOOK_INDEX+1
    SECOND_FACTOR_ENABLED_INDEX = FACEBOOK_INDEX+21 #34
    SECOND_FACTOR_METHODS_INDEX = FACEBOOK_INDEX+22 #35-38

    AUTHENTICATOR_APP_DEVICES_INDEX = FACEBOOK_INDEX+26
    PHONE_DEVICES_INDEX = FACEBOOK_INDEX+34
    SECURITY_KEY_DEVICES_INDEX = FACEBOOK_INDEX+37
    #ADDITIONAL_METHODS_INDEX = FACEBOOK_INDEX+48

    RECOVERY_METHODS_INDEX = FACEBOOK_INDEX+56
    RECOVERY_PHONE_DEVICES_INDEX = FACEBOOK_INDEX+58

    # Password access
    auth_nodes.append(parse_password_access(row, PASSWORD_ACCESS_INDEX))

    # Second factor
    if row[SECOND_FACTOR_ENABLED_INDEX] == "yes":
        second_factor = True

    if second_factor:
        for i in range(4):
            if not row[SECOND_FACTOR_METHODS_INDEX+i] == "":
                # parse devices
                devices = []
                if i == 0:
                    devices = parse_device_selection(
                        row, AUTHENTICATOR_APP_DEVICES_INDEX, 8)
                elif i == 1:
                    devices = parse_device_selection(
                        row, PHONE_DEVICES_INDEX, 3)
                elif i == 2:
                    devices = parse_device_selection(
                        row, SECURITY_KEY_DEVICES_INDEX, 10)
                elif i == 3:
                    devices = parse_device_selection(
                        row, ADDITIONAL_METHODS_INDEX, 8)
                auth_nodes.append(
                    {"nodeId": row[SECOND_FACTOR_METHODS_INDEX+i], "devices": devices})

    # Recovery
    for i in range(2):
        if not row[RECOVERY_METHODS_INDEX+i] == "":
            devices = []
            if i == 1:
                devices = parse_device_selection(
                    row, RECOVERY_PHONE_DEVICES_INDEX, 3)

            auth_nodes.append(
                {"nodeId": row[RECOVERY_METHODS_INDEX+i], "devices": devices})

    return {"auth_nodes": auth_nodes, "devices": deviceList}

def parse_Github_account(row):
    deviceList = parse_devices(row)

    auth_nodes = []
    second_factor = False
    passkeys = False

    PASSWORD_ACCESS_INDEX = GITHUB_INDEX+1
    PASSKEYS_ENABLED_INDEX = GITHUB_INDEX+21
    PASSKEYS_ENABLED_DEVICES_INDEX = GITHUB_INDEX+22
    SECOND_FACTOR_ENABLED_INDEX = GITHUB_INDEX+30
    SECOND_FACTOR_METHODS_INDEX = GITHUB_INDEX+31

    AUTHENTICATOR_APP_DEVICES_INDEX = GITHUB_INDEX+35
    PHONE_DEVICES_INDEX = GITHUB_INDEX+43
    SECURITY_KEY_DEVICES_INDEX = GITHUB_INDEX+46
    GITHUB_MOBILE_DEVICES_INDEX = GITHUB_INDEX+56

    RECOVERY_PRIMARY_INDEX = GITHUB_INDEX+59
    RECOVERY_CODES_INDEX = GITHUB_INDEX+60
    RECOVERY_CODES_DEVICES_INDEX = GITHUB_INDEX+61

    # Password access
    auth_nodes.append(parse_password_access(row, PASSWORD_ACCESS_INDEX))

    # Passkeys
    if row[PASSKEYS_ENABLED_INDEX] == "yes":
        passkeys = True

        if not row[PASSKEYS_ENABLED_DEVICES_INDEX] == "":
            devices = []
            devices = parse_device_selection(
                row, PASSKEYS_ENABLED_DEVICES_INDEX, 8)
            auth_nodes.append({"nodeId": "Passkeys", "devices": devices})

    # Second factor
    if row[SECOND_FACTOR_ENABLED_INDEX] == "yes":
        second_factor = True

    if second_factor:
        for i in range(4):
            if not row[SECOND_FACTOR_METHODS_INDEX+i] == "":
                # parse devices
                devices = []
                if i == 0:
                    devices = parse_device_selection(
                        row, AUTHENTICATOR_APP_DEVICES_INDEX, 8)
                elif i == 1:
                    devices = parse_device_selection(
                        row, PHONE_DEVICES_INDEX, 3)
                elif i == 2:
                    devices = parse_device_selection(
                        row, SECURITY_KEY_DEVICES_INDEX, 10)
                elif i == 3:
                    devices = parse_device_selection(
                        row, GITHUB_MOBILE_DEVICES_INDEX, 3)
                auth_nodes.append(
                    {"nodeId": row[SECOND_FACTOR_METHODS_INDEX+i], "devices": devices})

    # Recovery
    if row[RECOVERY_PRIMARY_INDEX] == "Yes":
        devices = []
        auth_nodes.append(
            {"nodeId": "recovery_email", "devices": devices})

    if row[RECOVERY_CODES_INDEX] == "Yes":
        devices = []
        devices = parse_device_selection(
            row, RECOVERY_CODES_DEVICES_INDEX, 3)
        auth_nodes.append(
            {"nodeId": "recovery_codes", "devices": devices})

    return {"auth_nodes": auth_nodes, "devices": deviceList}


def parse_Linkedin_account(row):
    deviceList = parse_devices(row)

    auth_nodes = []
    second_factor = False

    PASSWORD_ACCESS_INDEX = LINKEDIN_INDEX+1
    SECOND_FACTOR_ENABLED_INDEX = LINKEDIN_INDEX+21
    SECOND_FACTOR_METHODS_INDEX = LINKEDIN_INDEX+22

    AUTHENTICATOR_APP_DEVICES_INDEX = LINKEDIN_INDEX+23
    RECOVERY_KEYS_INDEX = LINKEDIN_INDEX+31
    RECOVERY_KEYS_DEVICES_INDEX = LINKEDIN_INDEX+32
    PHONE_DEVICES_INDEX = LINKEDIN_INDEX+40

    RECOVERY_METHODS_INDEX = LINKEDIN_INDEX+43
    RECOVERY_PHONE_DEVICES_INDEX = LINKEDIN_INDEX+45

    # Password access
    auth_nodes.append(parse_password_access(row, PASSWORD_ACCESS_INDEX))

    # Second factor
    if row[SECOND_FACTOR_ENABLED_INDEX] == "yes":
        second_factor = True

    if second_factor:
        if not row[SECOND_FACTOR_METHODS_INDEX] == "":
            # parse devices
            devices = []
            if row[SECOND_FACTOR_METHODS_INDEX] == "2fa_auth_app":
                devices = parse_device_selection(
                    row, AUTHENTICATOR_APP_DEVICES_INDEX, 8)
            elif row[SECOND_FACTOR_METHODS_INDEX] == "2fa_phone":
                devices = parse_device_selection(
                    row, PHONE_DEVICES_INDEX, 3)
            auth_nodes.append(
                {"nodeId": row[SECOND_FACTOR_METHODS_INDEX], "devices": devices})

    # Recovery
    for i in range(2):
        if not row[RECOVERY_METHODS_INDEX+i] == "":
            devices = []
            if i == 1:
                devices = parse_device_selection(
                    row, RECOVERY_PHONE_DEVICES_INDEX, 3)

            auth_nodes.append(
                {"nodeId": row[RECOVERY_METHODS_INDEX+i], "devices": devices})

    return {"auth_nodes": auth_nodes, "devices": deviceList}
