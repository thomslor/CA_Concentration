import sqlite3
import matplotlib.pyplot as plt
from difflib import SequenceMatcher
import dataframe_image as dfi
import pandas



def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def make_dico_ca(conn, type, rank):
    if type == "ca1":
        ca1_list = {}
        cursor = conn.execute("SELECT CA1, COUNT(URL) as f FROM CA_100K_6 WHERE RANK<=? AND CA1 != ? GROUP BY CA1 ORDER BY f DESC", (rank,""))
        for ca in cursor:
            ca1_list[ca[0]] = ca[1]
        return ca1_list

    elif type == "ca1_org":
        ca1_list = {}
        cursor = conn.execute("SELECT CA1_ORG, COUNT(URL) as f FROM CA_100K_6 WHERE RANK<=? AND CA1_ORG!=? GROUP BY CA1_ORG ORDER BY f DESC",
                              (rank,""))
        for ca in cursor:
            post = False
            for key in ca1_list.keys():
                if similar(ca[0], key) >= 0.9:
                    ca1_list[key] += ca[1]
                    post = True
                    break
            if not post:
                ca1_list[ca[0]] = ca[1]
        return {k: v for k, v in sorted(ca1_list.items(), key=lambda x: x[1], reverse=True)}

    elif type == "rca":
        rca_list = {}
        cursor = conn.execute("SELECT RCA, COUNT(URL) as f FROM CA_100K_6 WHERE RANK<=? AND RCA != ? GROUP BY RCA ORDER BY f DESC", (rank,""))
        for rca in cursor:
            rca_list[rca[0]] = rca[1]
        return rca_list

    elif type == "rca_org":
        rca_list = {}
        cursor = conn.execute("SELECT RCA_ORG, COUNT(URL) as f FROM CA_100K_6 WHERE RANK<=? AND RCA_ORG != ? GROUP BY RCA_ORG ORDER BY f DESC",
                              (rank,""))
        for rca in cursor:
            post = False
            for key in rca_list.keys():
                if similar(rca[0], key) >= 0.9:
                    rca_list[key] += rca[1]
                    post = True
                    break
            if not post:
                rca_list[rca[0]] = rca[1]
        return {k: v for k, v in sorted(rca_list.items(), key=lambda x: x[1], reverse=True)}

    else:
        print("Invalid Request")


def make_dico_doh_c(conn, country):
    ca1_list = {}
    cursor = conn.execute("SELECT CA1_ORG, COUNT(URL) as f FROM DOH WHERE COUNTRY == ? AND CA1_ORG != ? GROUP BY CA1_ORG ORDER BY f DESC",
                          (country,""))
    for ca in cursor:
        post = False
        for key in ca1_list.keys():
            if similar(ca[0], key) >= 0.9:
                ca1_list[key] += ca[1]
                post = True
                break
        if not post:
            ca1_list[ca[0]] = ca[1]
    return {k: v for k, v in sorted(ca1_list.items(), key=lambda x: x[1], reverse=True)}


def make_dico_ca_c(conn, type, country):
    if type == "ca1":
        ca1_list = {}
        cursor = conn.execute("SELECT CA1, COUNT(URL) as f FROM CA_100K_6 WHERE COUNTRY == ? AND CA1 != ? GROUP BY CA1 ORDER BY f DESC", (country,""))
        for ca in cursor:
            ca1_list[ca[0]] = ca[1]
        return ca1_list

    elif type == "ca1_org":
        ca1_list = {}
        cursor = conn.execute("SELECT CA1_ORG, COUNT(URL) as f FROM CA_100K_6 WHERE COUNTRY == ? AND CA1_ORG != ? GROUP BY CA1_ORG ORDER BY f DESC",
                              (country,""))
        for ca in cursor:
            post = False
            for key in ca1_list.keys():
                if similar(ca[0], key) >= 0.9:
                    ca1_list[key] += ca[1]
                    post = True
                    break
            if not post:
                ca1_list[ca[0]] = ca[1]
        return {k: v for k, v in sorted(ca1_list.items(), key=lambda x: x[1], reverse=True)}

    elif type == "rca":
        rca_list = {}
        cursor = conn.execute("SELECT RCA, COUNT(URL) as f FROM CA_100K_6 WHERE COUNTRY == ? AND RCA != ? GROUP BY RCA ORDER BY f DESC", (country,""))
        for rca in cursor:
            rca_list[rca[0]] = rca[1]
        return rca_list

    elif type == "rca_org":
        rca_list = {}
        cursor = conn.execute("SELECT RCA_ORG, COUNT(URL) as f FROM CA_100K_6 WHERE COUNTRY == ? AND RCA_ORG != ? GROUP BY RCA_ORG ORDER BY f DESC",
                              (country,""))
        for rca in cursor:
            post = False
            for key in rca_list.keys():
                if similar(rca[0], key) >= 0.9:
                    rca_list[key] += rca[1]
                    post = True
                    break
            if not post:
                rca_list[rca[0]] = rca[1]
        return {k: v for k, v in sorted(rca_list.items(), key=lambda x: x[1], reverse=True)}

    else:
        print("Invalid Request")


def make_dico_doh(conn, type):
    if type == "ca1":
        ca1_list = {}
        cursor = conn.execute("SELECT CA1, COUNT(DISTINCT SUBJECT) as f FROM DOH WHERE CA1 != ? GROUP BY CA1 ORDER BY f DESC", ("",))
        for ca in cursor:
            ca1_list[ca[0]] = ca[1]
        return ca1_list

    elif type == "ca1_org":
        ca1_list = {}
        cursor = conn.execute("SELECT CA1_ORG, COUNT(DISTINCT SUBJECT) as f FROM DOH WHERE CA1_ORG != ? GROUP BY CA1_ORG ORDER BY f DESC", ("",))
        for ca in cursor:
            post = False
            for key in ca1_list.keys():
                if similar(ca[0], key)>=0.9:
                    ca1_list[key] += ca[1]
                    post = True
                    break
            if not post:
                ca1_list[ca[0]] = ca[1]

        return {k: v for k, v in sorted(ca1_list.items(), key=lambda x: x[1], reverse=True)}

    elif type == "rca":
        rca_list = {}
        cursor = conn.execute("SELECT RCA, COUNT(DISTINCT SUBJECT) as f FROM DOH WHERE RCA != ? GROUP BY RCA ORDER BY f DESC", ("",))
        for rca in cursor:
            rca_list[rca[0]] = rca[1]
        return rca_list

    elif type == "rca_org":
        rca_list = {}
        cursor = conn.execute("SELECT RCA_ORG, COUNT(DISTINCT SUBJECT) as f FROM DOH WHERE RCA_ORG != ? GROUP BY RCA_ORG ORDER BY f DESC", ("",))
        for rca in cursor:
            post = False
            for key in rca_list.keys():
                if similar(rca[0], key) >= 0.9:
                    rca_list[key] += rca[1]
                    post = True
                    break
            if not post:
                rca_list[rca[0]] = rca[1]
        return {k: v for k, v in sorted(rca_list.items(), key=lambda x: x[1], reverse=True)}

    else:
        print("Invalid Request")


def make_graph(dico, number, type):
    labels = []
    values = []
    total = sum(dico.values())
    i = 0
    for k, v in sorted(dico.items(), key=lambda x: x[1], reverse=True):
        i += 1
        if i < 6:
            labels.append(f"{k}: {round((v/total)*100, 2)} %")
            values.append(v)
        else:
            labels.append("")
            values.append(v)
    plt.pie(values, labels=labels)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    fig.set_size_inches(12,6)

    if type == "ca":
        plt.title(f"CA distribution for the {number} most popular domains")
        plt.savefig("CAdistribution100K")
    elif type == "rca":
        plt.title(f"Root CA distribution for the {number} most popular domains")
        plt.savefig("RCAdistribution100K")
    elif type == "ca_org":
        plt.title(f"CAs' Organizations distribution for the {number} most popular domains")
        plt.savefig("CAOrgdistribution100K")
    elif type == "rca_org":
        plt.title(f"Root CAs' Organizations distribution for the {number} most popular domains")
        plt.savefig("RCAOrgdistribution100K")
    elif type == "doh_ca":
        plt.title(f"CA distribution for public DoH resolvers")
        plt.savefig("CAdistributionDOH")
    elif type == "doh_rca":
        plt.title(f"Root CA distribution for public DoH resolvers")
        plt.savefig("RCAdistributionDOH")
    elif type == "doh_ca_org":
        plt.title(f"CAs' Organizations distribution for public DoH resolvers")
        plt.savefig("CAOrgdistributionDOH")
    elif type == "doh_rca_org":
        plt.title(f"Root CAs' Organizations distribution for public DoH resolvers")
        plt.savefig("RCAOrgdistributionDOH")
    elif type == "country_url":
        plt.title(f"Country Distribution for the most popular HTTPS domains")
        plt.savefig("CountryURL")
    elif type == "country_doh":
        plt.title(f"Country Distribution for open DoH resolvers")
        plt.savefig("DOHcountry")

    plt.show()


def make_graph_c(dico, number, type, country):
    labels = []
    values = []
    total = sum(dico.values())
    i = 0
    for k, v in sorted(dico.items(), key=lambda x: x[1], reverse=True):
        i += 1
        if i < 6:
            labels.append(f"{k}: {round((v/total)*100, 2)} %")
            values.append(v)
        else:
            labels.append("")
            values.append(v)
    plt.pie(values, labels=labels)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    fig.set_size_inches(12,6)

    if type == "ca":
        plt.title(f'CA distribution for the {number} most popular domains for {country}')
        plt.savefig(f'CAdistribution100K{country}')
    elif type == "rca":
        plt.title(f'Root CA distribution for the {number} most popular domains for {country}')
        plt.savefig(f'RCAdistribution100K{country}')
    elif type == "ca_org":
        plt.title(f'CAs Organizations distribution for the {number} most popular domains for {country}')
        plt.savefig(f'CAOrgdistribution100K{country}')
    elif type == "rca_org":
        plt.title(f'Root CAs Organizations distribution for the {number} most popular domains for {country}')
        plt.savefig(f'RCAOrgdistribution100K{country}')
    elif type == "doh_ca":
        plt.title(f'CA distribution for public DoH resolvers for {country}')
        plt.savefig(f'CAdistributionDOH{country}')
    elif type == "doh_rca":
        plt.title(f'Root CA distribution for public DoH resolvers for {country}')
        plt.savefig(f'RCAdistributionDOH{country}')
    elif type == "doh_ca_org":
        plt.title(f'CAs Organizations distribution for public DoH resolvers for {country}')
        plt.savefig(f"CAOrgdistributionDOH{country}")
    elif type == "doh_rca_org":
        plt.title(f'Root CAs Organizations distribution for public DoH resolvers for {country}')
        plt.savefig(f'RCAOrgdistributionDOH{country}')
    elif type == "country_url":
        plt.title(f'Country Distribution for the most popular HTTPS domains for {country}')
        plt.savefig(f'CountryURL{country}')

    plt.show()


def modif_dico(dico, groups):
    new_dico = {'OTHERS':0}
    for name in dico.keys():
        if name not in groups:
            new_dico['OTHERS'] += dico[name]
        else:
            new_dico[name] = dico[name]
    return new_dico


def make_dico_country_url(conn, db):
    if db == "https":
        country = {}
        cursor = conn.execute("SELECT COUNTRY, COUNT(URL) FROM CA_100K_6 WHERE COUNTRY != ? AND COUNTRY != ? AND COUNTRY != ? AND length(COUNTRY) == ? GROUP BY COUNTRY",
                              ("None", "", "  ", 2))
        for row in cursor:
            country[row[0]] = row[1]
        return country
    elif db == "doh":
        country = {}
        cursor = conn.execute("SELECT COUNTRY, COUNT(DISTINCT URL) FROM DOH WHERE COUNTRY != ? AND COUNTRY != ? AND COUNTRY != ? AND length(COUNTRY) == ? GROUP BY COUNTRY",
                              ("None", "", "  ", 2))
        for row in cursor:
            country[row[0]] = row[1]
        return country
    else:
        print("Invalid")


def make_graph_distribution(conn, type):
    ca1 = []
    sum_ca1 = []
    ca1_modif = []

    for i in range(100, 100000, 100):
        dico = make_dico_ca(conn, type, i)
        ca1.append(dico)

    groups = [k for k, v in sorted(ca1[-1].items(), key=lambda x: x[1], reverse=True)]
    pop_groups = groups[:5]

    for dico in ca1:
        dico_m = modif_dico(dico, pop_groups)
        ca1_modif.append(dico_m)
        sum_ca1.append(sum(dico.values()))

    pop_groups.append("OTHERS")
    pop_dico = {}

    for group in pop_groups:
        pop_dico[group] = []
        for i in range(len(ca1)):
            pop_dico[group].append(ca1_modif[i][group] / sum_ca1[i])

    # print(pop_dico)

    scales = [i for i in range(100, 100000, 100)]
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray',
              'tab:olive', 'tab:cyan', 'w']

    for group in pop_dico.keys():
        plt.plot(scales, pop_dico[group])
    plt.legend(loc='upper right', labels=[group for group in pop_dico.keys()], title='CA',
               bbox_to_anchor=(1, 1), fontsize=7.5)
    if type == "ca1_org":
        plt.title("Distribution of CAs Organizations for HTTPS depending on rank")
        plt.savefig("Distribution of CAs Org for HTTPS")
        plt.show()
    elif type == "rca_org":
        plt.title("Distribution of Root CAs Organizations for HTTPS depending on rank")
        plt.savefig("Distribution of Root CAs Org for HTTPS")
        plt.show()


def make_table_country(conn, type, title):
    dicos = {}
    dico = make_dico_country_url(conn, type)
    groups = [k for k, v in sorted(dico.items(), key=lambda x: x[1], reverse=True)]
    pop_groups = groups[:5]
    for country in pop_groups:
        ca_p = []
        if type == "https":
            dico_country = make_dico_ca_c(conn, "ca1_org", country)
        elif type == "doh":
            dico_country = make_dico_doh_c(conn, country)
        sum_dico_country = sum(dico_country.values())
        keys = list(dico_country.keys())[:5]
        for key in keys:
            ca_p.append(f"{key} : {round((dico_country[key]/sum_dico_country)*100)} %")
        dicos[country] = ca_p

    ca_p = []
    if type == "https":
        dico_global = make_dico_ca(conn, "ca1_org", 100000)
    elif type == "doh":
        dico_global = make_dico_doh(conn, "ca1_org")
    sum_dico_global = sum(dico_global.values())
    keys = list(dico_global.keys())[:5]
    for key in keys:
        ca_p.append(f"{key} : {round((dico_global[key] / sum_dico_global) * 100)} %")
    dicos["Global"] = ca_p
    print(dicos)
    df = pandas.DataFrame.from_dict(dicos)
    df_styled = df.style.background_gradient()
    dfi.export(df_styled, title)


if __name__ == '__main__':

    conn = sqlite3.connect('ca.db')

    make_table_country(conn, "doh", "Table for DoH.png")
    make_table_country(conn, "https", "Table for HTTPS.png")


    make_graph(make_dico_ca(conn, "ca1_org", 100000), 100000, "ca_org")
    make_graph(make_dico_ca(conn, "rca_org", 100000), 100000, "rca_org")
    make_graph(make_dico_ca(conn, "ca1", 100000), 100000, "ca")
    make_graph(make_dico_ca(conn, "rca", 100000), 100000, "rca")

    make_graph(make_dico_doh(conn, "ca1"), 0, "doh_ca")
    make_graph(make_dico_doh(conn, "rca"), 0, "doh_rca")
    make_graph(make_dico_doh(conn, "ca1_org"), 0, "doh_ca_org")
    make_graph(make_dico_doh(conn, "rca_org"), 0, "doh_rca_org")

    make_graph_distribution(conn, "ca1_org")
    make_graph_distribution(conn, "rca_org")
    make_graph(make_dico_country_url(conn, "https"), 0, "country_url")
    make_graph(make_dico_country_url(conn, "doh"), 0, "country_doh")








