import ssl
import socket
import traceback
import sqlite3
import time
import multiprocessing
import whois
import dns.resolver
import geoip2.database
import geoip2.errors
import sys


def get_ip(domain):
    try:
        result = dns.resolver.resolve(domain, 'A')
        IP = result[0].to_text()
        return IP

    except dns.resolver.NoAnswer:
        print(f"Pas de réponse IP pour dns : {domain}")

    except dns.exception.Timeout:
        print(f"Timeout pour DNS Request : {domain}")

    except dns.resolver.NXDOMAIN:
        print(f"DNS name does not exist for {domain}")

    except dns.resolver.NoNameservers:
        print(f"No response for: {domain}")

    return None


def get_domains(start, end):
    with open("alexa-top1m-2022-11-02_0900_UTC.csv", 'r') as f:
        lines = f.readlines()
        return [lines[i].rstrip() for i in range(start, end)]


def check_country(info):
    for sublist in info:
        for element in sublist:
            if 'countryName' in element:
                return element[1]
    return "None"


def check_organization(info):
    for sublist in info:
        for element in sublist:
            if 'organizationName' in element:
                return element[1]
    return "None"


def check_cn(info):
    for sublist in info:
        for element in sublist:
            if 'commonName' in element:
                if element[1] != "":
                    return element[1]
    return "None"


def insert_db(domain,rank,subject,country, CA1, CA1_ORG, CA1_C, ICA, ICA_ORG, ICA_C, RCA, RCA_ORG, RCA_C):
    c.execute('''INSERT INTO CA_100K_6U(URL, RANK, SUBJECT, COUNTRY, CA1, CA1_ORG, CA1_C, ICA, ICA_ORG, ICA_C, RCA, RCA_ORG, RCA_C) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (str(domain),
               rank,
               str(subject),
               str(country),
               str(CA1),
               str(CA1_ORG),
               str(CA1_C),
               str(ICA),
               str(ICA_ORG),
               str(ICA_C),
               str(RCA),
               str(RCA_ORG),
               str(RCA_C),
               ))
    conn.commit()


def current_db(cursor):
    list_db = []
    cursor.execute("SELECT URL FROM CA_100K_6U")
    for domain in cursor:
        list_db.append(domain[0])
    return list_db


def get_ca(domain, rank, shared_list, list_error, countrycode, cipher=False):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        if cipher:
            ctx.set_ciphers('DEFAULT')

        # Handshake as normal, still set `server_hostname` for SNI
        sock = socket.create_connection((domain, 443), timeout=5)
        # print(sock.gettimeout())
        sock = ctx.wrap_socket(sock, server_hostname=domain)
        cert_chain = sock._sslobj.get_unverified_chain()
        subject = ""
        country = ""
        ca1 = ""
        ca1_org = ""
        ca1_c = ""
        ica = ""
        ica_org = ""
        ica_c = ""
        rca = ""
        rca_org = ""
        rca_c = ""
        for i in range(0, len(cert_chain)):
            info = cert_chain[i].get_info()
            if i == 0:
                country = check_country(info['subject'])
                if country == "None" or country == "--" or country == "  " or len(country) != 2:
                    try:
                        country = whois.whois(domain)['country']
                    except KeyError:
                        if domain.split(".")[-1].upper() in countrycode:
                            country = domain.split(".")[-1].upper()
                        else:
                            with geoip2.database.Reader('./GeoLite2-Country_20221115/GeoLite2-Country.mmdb') as reader:
                                try:
                                    answer = reader.country(domain)
                                    country = answer.country.iso_code
                                except:
                                    country = "None"
                subject = check_cn(info['subject'])
                # print(subject)
                # print(country)
            elif i == 1:
                ca1 = check_cn(info['subject'])
                # print(ca1)
                ca1_org = check_organization(info['subject'])
                # print(ca1_org)
                ca1_c = check_country(info['subject'])
                # print(ca1_c)
            elif i == len(cert_chain) - 1:
                rca = check_cn(info['subject'])
                # print(rca)
                rca_org = check_organization(info['subject'])
                # print(rca_org)
                rca_c = check_country(info['subject'])
                # print(rca_c)
            else:
                if ica == "":
                    ica = check_cn(info['subject'])
                    # print(ica)
                    ica_org = check_organization(info['subject'])
                    # print(ica_org)
                    ica_c = check_country(info['subject'])
                    # print(ica_c)
                else:
                    ica += "/" + check_cn(info['subject'])
                    # print(ica)
                    ica_org += "/" + check_organization(info['subject'])
                    # print(ica_org)
                    ica_c += "/" + check_country(info['subject'])
                    # print(ica_c)

        shared_list.append(tuple([domain, rank, subject, country, ca1, ca1_org, ca1_c, ica, ica_org, ica_c, rca, rca_org, rca_c]))
        # insert_db(domain, rank, subject, country, ca1, ca1_org, ca1_c, ica, ica_org, ica_c, rca, rca_org, rca_c)



    except Exception:
        list_error.append(sys.exc_info()[0])
        if not cipher:
            get_ca(domain, rank, shared_list, list_error, countrycode, True)
        pass


def get_ca_list(domains, shared_list, list_db, list_error, countrycode):
    for domain in domains:
        rank = domain.split(',')[0]
        domain = domain.split(',')[1]
        if domain not in list_db:
            if "www."+domain not in list_db:
                print(f"Research for {domain}".format(domain=domain))
                if "www." not in domain:
                    domain = "www."+domain
                get_ca(domain, rank, shared_list, list_error, countrycode)
                print("================================================")
            else:
                print("www.{domain} already in DB".format(domain=domain))
        else:
            print("{domain} already in DB".format(domain=domain))

if __name__ == "__main__":
    conn = sqlite3.connect('ca.db')
    c = conn.cursor()

    conn.execute('''CREATE TABLE if not exists CA_100K_6U
                (URL TEXT NOT NULL,
                RANK INT,
                SUBJECT TEXT,
                COUNTRY TEXT,
                CA1 TEXT,
                CA1_ORG TEXT,
                CA1_C TEXT,
                ICA TEXT,
                ICA_ORG TEXT,
                ICA_C TEXT,
                RCA TEXT,
                RCA_ORG TEXT,
                RCA_C TEXT);''')

    domains = get_domains(0, 100000)
    print(domains)
    list_db = current_db(c)
    print(list_db)
    countrycode = []

    with open("countrycode.csv", 'r') as f:
        lines = f.readlines()
        tab = [lines[i].rstrip() for i in range(0, len(lines))]
        for el in tab:
            countrycode.append(el.split(",")[-1])



    manager = multiprocessing.Manager()
    process_num = 10
    print('Process number: ' + str(process_num))
    shared_list = manager.list()
    list_error = manager.list()
    workers = []
    start_list = 0
    end_range = int(100000 / process_num)
    end_list = end_range

    start = time.time()

    for t in range(0, process_num):
        print(start_list)
        print(end_list)
        domains = get_domains(start_list, end_list)
        p = multiprocessing.Process(target=get_ca_list, args=(domains, shared_list, list_db, list_error, countrycode))
        p.start()
        workers.append(p)
        start_list = end_list + 1
        end_list += end_range

    for p in workers:
        p.join()

    for item in shared_list:
        insert_db(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11], item[12])

    dict_errors = {}
    for item in list_error:
        if item not in dict_errors.keys():
            dict_errors[item] = 1
        else:
            dict_errors[item] += 1

    with open("errors.txt", "w") as f:
        for error_type in dict_errors:
            f.write(f"{str(error_type)}:{dict_errors[error_type]}")


    print("--- %s seconds ---" % (time.time() - start))






