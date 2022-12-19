import ssl
import socket
import traceback
import sqlite3
import time
import multiprocessing
import geoip2.database
import geoip2.errors


def get_domains(start):
    doh_list = []
    with open("list-of-doh-servers-internet-April-2021.csv", 'r') as f:
        lines = f.readlines()
        end = len(lines)
        tab = [lines[i].rstrip() for i in range(start, end)]
        for doh in tab:
            doh_list.append(doh.split(",")[1])
    with open("DoH Internet Servers Dataset.csv", 'r') as f:
        lines = f.readlines()
        end = len(lines)
        tab = [lines[i].rstrip() for i in range(start, end)]
        for doh in tab:
            doh_list.append(doh.split(",")[0])
    return doh_list


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


def insert_db(domain,subject,country, CA1, CA1_ORG, CA1_C, ICA, ICA_ORG, ICA_C, RCA, RCA_ORG, RCA_C):
    c.execute('''INSERT INTO DOH(URL, SUBJECT, COUNTRY, CA1, CA1_ORG, CA1_C, ICA, ICA_ORG, ICA_C, RCA, RCA_ORG, RCA_C) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (str(domain),
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
    cursor.execute("SELECT URL FROM DOH")
    for domain in cursor:
        list_db.append(domain[0])
    return list_db


def get_ca(domain, shared_list, cipher=False):
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        if cipher:
            ctx.set_ciphers('DEFAULT')

        # Handshake as normal, still set `server_hostname` for SNI
        sock = socket.create_connection((domain, 443), timeout=5)
        # print(sock.gettimeout())
        sock = ctx.wrap_socket(sock)
        cert_chain = sock._sslobj.get_verified_chain()
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
                if country == "None" or country == "--":
                    with geoip2.database.Reader('./GeoLite2-Country_20221115/GeoLite2-Country.mmdb') as reader:
                        try:
                            answer = reader.country(domain)
                            country = answer.country.iso_code
                        except geoip2.errors.AddressNotFoundError:
                            print('IP not in Database')
                        except ValueError:
                            print("Problème avec l'IP")
                        except Exception:
                            traceback.print_exc()
                            pass
                subject = check_cn(info['subject'])
                print(subject)
                print(country)
            elif i == 1:
                ca1 = check_cn(info['subject'])
                print(ca1)
                ca1_org = check_organization(info['subject'])
                print(ca1_org)
                ca1_c = check_country(info['subject'])
                print(ca1_c)
            elif i == len(cert_chain) - 1:
                rca = check_cn(info['subject'])
                print(rca)
                rca_org = check_organization(info['subject'])
                print(rca_org)
                rca_c = check_country(info['subject'])
                print(rca_c)
            else:
                if ica == "":
                    ica = check_cn(info['subject'])
                    print(ica)
                    ica_org = check_organization(info['subject'])
                    print(ica_org)
                    ica_c = check_country(info['subject'])
                    print(ica_c)
                else:
                    ica += "/" + check_cn(info['subject'])
                    print(ica)
                    ica_org += "/" + check_organization(info['subject'])
                    print(ica_org)
                    ica_c += "/" + check_country(info['subject'])
                    print(ica_c)

        shared_list.append(tuple([domain, subject, country, ca1, ca1_org, ca1_c, ica, ica_org, ica_c, rca, rca_org, rca_c]))
        # insert_db(domain, rank, subject, country, ca1, ca1_org, ca1_c, ica, ica_org, ica_c, rca, rca_org, rca_c)



    except Exception:
        traceback.print_exc()
        if not cipher:
            get_ca(domain, shared_list, True)
        pass


def get_ca_list(domains, shared_list, list_db):
    for domain in domains:
        if domain not in list_db:
            get_ca(domain, shared_list)
        else:
            print("{domain} already in DB".format(domain=domain))


if __name__ == "__main__":
    conn = sqlite3.connect('ca.db')
    c = conn.cursor()

    conn.execute('''CREATE TABLE if not exists DOH
                (URL TEXT NOT NULL,
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

    domains = get_domains(1)
    print(domains)
    list_db = current_db(c)
    print(list_db)

    manager = multiprocessing.Manager()
    process_num = 1
    print('Process number: ' + str(process_num))
    shared_list = manager.list()
    workers = []

    start = time.time()

    domains = get_domains(1)
    p = multiprocessing.Process(target=get_ca_list, args=(domains, shared_list, list_db))
    p.start()
    workers.append(p)


    for p in workers:
        p.join()

    for item in shared_list:
        insert_db(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11])



    print("--- %s seconds ---" % (time.time() - start))




