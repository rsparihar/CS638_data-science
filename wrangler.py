# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as bs
from itertools import izip as iz
from glob import glob
from datetime import datetime as dt
import csv, re, sys, traceback

__authors__ = ["rsparihar"]

HTML_PARSER = "html.parser"
CLASS = "class"
ROTTEN_COLUMNS_FIELD_CLASS = "col col-sm-5 col-xs-10 clearfix subtle bold"
ROTTEN_COLUMNS_VAL_CLASS = ""
ROTTEN_CSV_FILE = "rotten_movies.csv"
TMDB_CSV_FILE = "tmdb.csv"
rotten_files = glob("./rotten/*.html")
tmdb_files = glob("./tmdb/*.html")
rotten_dict_data_full = []
tmdb_dict_data_full = []
rotten_csv_header_flag = 1
tmdb_csv_header_flag = 1


def parse_html(html_file, mode) :
    tmdb_dc = {}
    rotten_dc = {}
    try:
        f = bs(open(html_file), HTML_PARSER)
        parentNode = ""
        movie_title = f.find("meta", attrs={"property": "og:title"})['content']
        movie_partial_url = f.find("meta", attrs={"property": "og:url"})['content'].split("/")[4]
    except Exception as e:
            print e
            return -1

    if mode == "rotten" :
        tag_name = "div"
        class_val = "info"
        try :
            parentNode = f.find(tag_name, attrs={CLASS : class_val})
            raw_rotten_data = []
            if not parentNode :
                print "Error(s) encountered while parsing ", tag_name," in - ", html_file, ". Continuing to next html file."
                return -1
            for rotten_ele in parentNode.findAll("div") :
                if not rotten_ele :
                    print "Error(s) encountered while parsing div in - ", html_file, ". Continuing to next html file."
                    return -1
                y = str(rotten_ele.text.encode('utf-8').strip().replace("\n\n",""))
                if y.endswith(":"):
                    y = y.replace(":","")
                raw_rotten_data.append(y)
            i1 = iter(raw_rotten_data)
            rotten_dc = dict(iz(i1,i1))
            rotten_out_dict = {}
            rotten_out_dict["Title"] = movie_title
            rotten_out_dict["Rating"] = rotten_dc.get("Rating","NOT_AVAILABLE").split()[0]
            rotten_out_dict["ReleaseDate"] = rotten_dc.get("In Theaters", "Dec 31,9999")
            if rotten_out_dict["ReleaseDate"] != "Dec 31,9999" :
                rotten_out_dict["ReleaseDate"] = dt.strptime(rotten_dc.get("In Theaters", "Dec 31,9999").split("\n")[0],"%b %d, %Y")
            #rotten_out_dict["Writers"] = ','.join(re.compile("(\,\\s*)+").split(rotten_dc.get("Written By", "NOT_AVAILABLE").replace("\n",",")))
            rotten_out_dict["Writers"] = rotten_dc.get("Written By", "NOT_AVAILABLE").replace("\n","")
            rotten_out_dict["Directors"] = rotten_dc.get("Directed By", "NOT_AVAILABLE").replace("\n","")
            rotten_out_dict["Genre"] = rotten_dc.get("Genre", "NOT_AVAILABLE").replace("\n","")
            rotten_out_dict["Revenue"] = rotten_dc.get("Box Office",0.0)
            rotten_out_dict["Runtime"] = rotten_dc.get("Runtime",0)
            rotten_out_dict["PartialURL"] = movie_partial_url
            print rotten_dc
            rotten_dict_data_full.append(rotten_out_dict)
        except Exception as e:
            print e
            print "Error(s) encountered while parsing - ", html_file, ". Continuing to next html file."
            return -1

    elif mode == "tmdb" :
        tag_name = "section"
        class_val = "facts"
        try :
            parentNode = f.find(tag_name, attrs={CLASS: class_val})
            if not parentNode :
                print "Error(s) encountered while parsing",tag_name,"in - ",html_file,".Continuing to next html file."
                return -2
            for tmdb_ele in parentNode.findAll("strong"):
                if not tmdb_ele :
                    print "Error(s) encountered while parsing <strong> in -",html_file,".Continuing to next html file."
                    return -2
                attrib = tmdb_ele.text.encode("utf-8").strip()
                val = tmdb_ele.next_sibling
                if attrib == "Rating" and val :
                    val = val.split()[0]
                if val :
                    tmdb_dc[attrib] = val.encode("utf-8").strip()
            ul_node = parentNode.find("ul")
            li_node = None
            release_date = "December 31,9999"
            rating = "NOT_AVAILABLE"
            if ul_node:
                li_node = ul_node.find("li")
            if li_node :
                release_date_info = parentNode.find("ul").find("li").text.encode("utf-8").strip().split("\n")
                release_date = dt.strptime(release_date_info[0], "%B %d, %Y")
                rating = release_date_info[1].split(",")[0]
            tmdb_dc["Release Date"] = release_date
            tmdb_dc["Rating"] = rating
            writers = []
            directors = []
            character_nodes = f.find("ol", attrs={"class":"people"}).findAll("li",attrs={"class":"profile"})
            for character_node in character_nodes :
                character = character_node.find("p").text.encode("utf-8")
                roles_str = character_node.find("p", attrs={"class":"character"}).text.encode("utf-8")
                roles = re.compile("(\,\\s*)+").split(roles_str)
                for role in roles :
                    if role == "Screenplay" or role == "Writer" :
                        writers.append(character)
                    elif role == "Director" :
                        directors.append(character)
            genres = []
            genres_node = f.find("section", attrs={"class":"genres"}).find("ul").findAll("li")
            for genre in genres_node:
                genres.append(genre.text.encode("utf-8"))
            print tmdb_dc
            tmdb_out_dict = {}
            tmdb_out_dict["Title"] = movie_title
            tmdb_out_dict["Rating"] = tmdb_dc.get("Rating", "NOT_AVAILABLE")
            tmdb_out_dict["ReleaseDate"] = tmdb_dc.get("Release Date", "December 31,9999")
            tmdb_out_dict["Writers"] = ','.join(writers)
            tmdb_out_dict["Directors"] = ','.join(directors)
            tmdb_out_dict["Genre"] = ','.join(genres)
            tmdb_out_dict["Revenue"] = tmdb_dc.get("Revenue", -1.0)
            tmdb_out_dict["Runtime"] = tmdb_dc.get("Runtime", "-1 minutes")
            tmdb_out_dict["PartialURL"] = movie_partial_url
            tmdb_dict_data_full.append(tmdb_out_dict)
        except Exception as e:
            print e
            print "Error(s) encountered while parsing - ", html_file, ". Continuing to next html file."
            return -2


def write_to_csv(csv_file, mode, data) :                                # data is an array of dictionaries
    global rotten_csv_header_flag
    global tmdb_csv_header_flag
    with open(csv_file, 'w') as csvfile:
        fieldnames = ["Title", "Rating", "ReleaseDate", "Writers", "Directors", "Genre", "Revenue", "Runtime", "PartialURL"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if mode == "rotten" and rotten_csv_header_flag == 1 :
            try :
                writer.writeheader()
            except Exception as e:
                print e
                print "Error(s) encountered while writing data to - ", csv_file, "."
                print "Fields/Header data - ", fieldnames, ". Continuing to write data row."
            rotten_csv_header_flag = 0
        elif mode == "tmdb" and tmdb_csv_header_flag == 1 :
            try :
                writer.writeheader()
            except Exception as e:
                print e
                print "Error(s) encountered while writing data to - ", csv_file, "."
                print "Fields/Header data - ", fieldnames, ". Continuing to write data row."
            tmdb_csv_header_flag = 0

        for row in data:
            try :
                writer.writerow(row)
            except Exception as e:
                print e
                print "Error(s) encountered while writing data to - ", csv_file, "."
                print "Row data - ", row, ". Continuing to write next row."

start = dt.now()
for html_file in rotten_files :
    parse_html(html_file, "rotten")
write_to_csv(ROTTEN_CSV_FILE, "rotten", rotten_dict_data_full)
for html_file in tmdb_files :
    parse_html(html_file, "tmdb")
write_to_csv(TMDB_CSV_FILE, "tmdb", tmdb_dict_data_full)
end = dt.now()
print 'time taken = ', end-start

