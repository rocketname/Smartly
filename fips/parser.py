# coding=utf-8

import re
import html as lib_html
import requests

databases = ("RUTM")
document_url = "http://www1.fips.ru/fips_servl/fips_servlet"

RE_IMAGE = re.compile('<IMG SRC="(.+-s.jpg)?" BORDER="0">')
RE_REG_NUM = re.compile("\(111\).+?<B>(\d+)</B>")
RE_APP_NUM = re.compile("\(210\).+?<B>(\d+)</B>")
RE_RIGHT_HOLDER = re.compile("\(732\).+?<B>([\w\W]+?)</B>")
RE_ADDRESS_POSTAL = re.compile("\(750\).+?<B>([\w\W]+?)</B>")

RE_DATE_APP = re.compile("\(220\).+?<B>([\d\.]+)</B>")
RE_DATE_EXPIRED = re.compile("\(181\).+?\W.+<B>([\d\.]+?)</B>")
RE_DATE_PRIORITY = re.compile("<I>Приоритет:</I> <B>([\d\.]+)</B>")
RE_DATE_PUBLISHED = re.compile("\(450\).+?PDF'>([\d\.]+?)<")
RE_DATE_REGISTERED = re.compile("\(151\).+?\W.+?<B>([\d\.]+)</B>")

RE_EVENT_TYPE = re.compile("<B>(Государственная регистрация.+?)</B>")
RE_EVENT_DATE = re.compile("PDF'>([\d\.]+?)</A>")
RE_EVENT_FIELDS = re.compile(
"<BR><BR>(.*?)<I>(?P<field>.*?):</I>(?:<BR>|<BR />|\W?)+"
"<B>(?P<value>.*?)</B>\W"
)


class FipsError(BaseException):
    def __init__(self, message):
        self.message = message


        class FipsItem(object):
            """ FIPS TradeMark item
            """
            __slots__ = (
            "image", "reg_num", "app_num", "right_holder", "address_postal",
            "date_app", "date_expired", "date_priority", "date_published",
            "date_registered", "events"
            )

            def __init__(self, reg_num, app_num, image, right_holder, address_postal,
            date_app, date_expired, date_priority, date_published,
            date_registered, events=None):
            self.image = image
            self.reg_num = int(reg_num)
            self.app_num = int(app_num)
            self.right_holder = right_holder
            self.address_postal = address_postal
            self.date_app = date_app
            self.date_expired = date_expired
            self.date_priority = date_priority
            self.date_published = date_published
            self.date_registered = date_registered

            self.events = events

            def __repr__(self):
                items = []
                for attr in self.__slots__:
                    items.append("{:20s}: {}".format(attr, getattr(self, attr)))
                    return "\n".join(items)


                    def load(database, reg_number):
                        """ Create FipsItem from remote document
                        """
                        if database not in databases:
                            raise FipsError("Invalid database '{}'. Valid choices: {}".format(
                            database, databases))

                            params = {"DB": database, "DocNumber": reg_number, "TypeFile": "html"}
                            r = requests.get(document_url, params=params)
                            if r.status_code != 200:
                                raise FipsError("Invalid remote status: {}".format(r.status))

                                return parse_document(r.text)


                                def parse_document(document):
                                    """ Parse full document
                                    """
                                    try:
                                        item, events = document.split('Извещения об изменениях')
                                        item = parse_item(item)
                                        item.events = parse_events(events)
                                    except:
                                        item = parse_item(document)

                                        return item


                                        def parse_item(html):
                                            """ Parse main item
                                            """
                                            right_holder = RE_RIGHT_HOLDER.findall(html)[0]
                                            right_holder = " ".join(lib_html.unescape(right_holder).split())
                                            address_postal = " ".join(RE_ADDRESS_POSTAL.findall(html)[0].split())

                                            return FipsItem(
                                            image=RE_IMAGE.findall(html)[0],
                                            reg_num=RE_REG_NUM.findall(html)[0],
                                            app_num=RE_APP_NUM.findall(html)[0],
                                            right_holder=right_holder,
                                            address_postal=address_postal,

                                            date_app=RE_DATE_APP.findall(html)[0],
                                            date_expired=RE_DATE_EXPIRED.findall(html)[0],
                                            date_priority=RE_DATE_PRIORITY.findall(html)[0],
                                            date_published=RE_DATE_PUBLISHED.findall(html)[0],
                                            date_registered=RE_DATE_REGISTERED.findall(html)[0],
                                            )


                                            def parse_events(events):
                                                """ Parse item events
                                                """
                                                result = list()
                                                events = events.replace("\n", "")\
                                                .split('<HR STYLE="color:black; height:1px;">')[1:]

                                                for event in events:
                                                    try:
                                                        match = RE_EVENT_FIELDS.findall(event)
                                                        event_data = {"Тип": RE_EVENT_TYPE.findall(event)[0].strip(),
                                                        "Дата": RE_EVENT_DATE.findall(event)[0].strip()}
                                                        for item in match:
                                                            field = item[1]
                                                            value = " ".join(lib_html.unescape(item[2]).split())
                                                            event_data[field] = value
                                                            result.append(event_data)
                                                        except:
                                                            continue
                                                            return result
