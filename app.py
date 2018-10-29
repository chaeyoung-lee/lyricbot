#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import json
import urllib.request, urllib.error, urllib.parse
import socket
from flask import Flask, request, g
import random
import requests
import lyricwikia

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "No personal information is gathered. This bot is part of my personal project. Contact: limetree377@gmail.com", 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    if "text" in messaging_event["message"]:
                        message_text = messaging_event["message"]["text"][0:]  # the message's text

                        if keyword(message_text) != None:
                            send_message(sender_id, keyword(message_text))
                        else:
                            a = lyric_message(sender_id, message_text)
                            if a == 0:
                                send_message(sender_id, "Sorry! My DB doesn't contain that song...")
                                start_message(sender_id)
                    elif "sticker_id" in messaging_event["message"]:
                        sticker_id = messaging_event["message"]["sticker_id"]
                        if sticker_id == 369239263222822 or sticker_id == 369239383222810 or sticker_id == 369239343222814:
                            send_message(sender_id, "Thanks for the like!")
                        else:
                            send_message(sender_id, "cool.")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message

                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]
                    postback = messaging_event["postback"]["payload"]

                    if postback == "GET_STARTED_PAYLOAD":
                        start_message(sender_id)
                    elif postback == "SEARCH":
                        send_message(sender_id, "What is the artist and song title?\ntype in: (artist) - (title)\nex) kendrick lamar - i")
                    elif postback == "INTRO":
                        send_message(sender_id, "Hi, I'm LyricBot. I see that you want to know about me.")
                        send_message(sender_id, "I'm a lyric search chatbot. I was created by Chae Young Lee, a South Korean rapper. If you enjoy talking to me - although I don't really make sense - plz press LIKE for my page!")
                    elif postback == "CHART":
                        chart = chart_search(1)
                        chart_message1(sender_id, chart)
                    elif postback == "MORE1":
                        chart = chart_search(2)
                        chart_message2(sender_id, chart)
                    elif postback == "MORE2":
                        chart = chart_search(3)
                        chart_message3(sender_id, chart)
                    elif postback == "MORE3":
                        chart = chart_search(4)
                        chart_message4(sender_id, chart)
                    elif postback == "MORE4":
                        chart = chart_search(5)
                        chart_message5(sender_id, chart)
                    elif postback == "MORE5":
                        chart = chart_search(6)
                        chart_message6(sender_id, chart)
                    elif postback == "MORE6":
                        chart = chart_search(7)
                        chart_message7(sender_id, chart)
                    elif postback == "MORE7":
                        chart = chart_search(8)
                        chart_message8(sender_id, chart)
                    elif postback == "MORE8":
                        chart = chart_search(9)
                        chart_message9(sender_id, chart)
                    elif postback == "MORE9":
                        chart = chart_search(10)
                        chart_message10(sender_id, chart)
                    else:
                        lyric_message(sender_id, postback)

    return "ok", 200

# sending message
def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
def start_message(recipient_id):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text="Suggestion for the lyrics."))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Hi! I'm LyricBot. What would you like to do?",
                    "buttons": [
                        {
                            "type": "postback",
                            "title": "Search Lyrics",
                            "payload": "SEARCH"
                        },
                        {
                            "type": "postback",
                            "title": "Who Are You?",
                            "payload": "INTRO"
                        },
                        {
                            "type": "postback",
                            "title": "Music Chart",
                            "payload": "CHART"
                        }

                    ]
                }
            }
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)
def lyric_message(sender_id, query):
    a = get_lyrics(query)

    if a == 0:     # no lyrics found
        return a

    # FB does not allow message length over 600 letters :(
    num = int(len(a) / 600)

    for i in range(1, num + 2):
        start = 600 * (i - 1)
        end = 600 * i
        send_message(sender_id, a[start:end])
def chart_message1(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "http://www.drodd.com/images15/1-12.jpg",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://woolacombe.devon.sch.uk/wp-content/uploads/2013/12/number-2-vector-447287.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "http://www.fiestasatuaire.es/wp-content/uploads/2017/01/Sala-3-600x470.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "https://www.astrogle.com/images/2014/09/number-47.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE1"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message2(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "http://www.drodd.com/images15/5-18.jpg",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://www.hamiltonundergroundpress.com/uploads/4/9/5/0/49501305/3236077_orig.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "http://www.drodd.com/images15/7-20.png",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "http://www.drodd.com/images15/8-3.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE2"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message3(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "http://www.drodd.com/images15/9-4.png",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "https://10.unpri.org/wp-content/themes/PRI/inc/img/10_logo_home.png",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "https://www.snapsurveys.com/blog/wp-content/uploads/2013/06/snap-11-logo-5000px-1024x1024.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "https://carbon12dubai.com/wp-content/uploads/12.png",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE3"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message4(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "http://raisingteensblog.com/wp-content/uploads/2017/03/13.jpg",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://www.drodd.com/images15/14-14.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "http://www.drodd.com/images15/15-17.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "https://i.pinimg.com/736x/15/b1/21/15b12166d65e1ec0d99656f52ba075f9--gold--balloons-sweet--balloons.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE4"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message5(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "https://silverbirchpress.files.wordpress.com/2016/12/17.jpg?w=460",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://www.drodd.com/images15/18-15.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "http://work.studioaad.com/wp-content/uploads/2012/01/GR19Logo.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "https://i.pinimg.com/originals/ab/d5/76/abd57686e3d9ae47be1fc86714768b25.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE5"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message6(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "http://www.21hospitality.co.uk/wp-content/uploads/2011/02/21-Logo.jpg",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://mathematics-in-europe.eu/wp-content/uploads/2016/02/cursive-number-22.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "https://i.pinimg.com/736x/e5/a7/37/e5a73755c3f696d2c3077ce66f55b979--number-tattoo-fonts--tattoo-number.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "https://fiftytwopoetry.files.wordpress.com/2014/06/24.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE6"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message7(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "http://wau14.com/WAUUSA/wp-content/uploads/2016/12/25-004-375x372.jpg",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://www.drodd.com/images16/26-3.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "https://pbs.twimg.com/profile_images/517836755748147200/kmvUaCjb.png",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "http://www.atlascorps.org/blog/wp-content/uploads/2016/04/177151-number-28.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE7"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message8(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "http://mom.girlstalkinsmack.com/image/092012/He%27s%2029_1.jpg",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://www.drodd.com/images16/30-7.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "http://www.drodd.com/images16/30-1.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "https://www.ridefox.com/2016/img/family/bike/32-stepcast-logo.png",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE8"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message9(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "https://media.licdn.com/mpr/mpr/p/6/005/07f/318/07002e6.jpg",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://www.drodd.com/images16/34-12.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "http://mediad.publicbroadcasting.net/p/wvpn/files/201403/US35.png",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "https://pbs.twimg.com/profile_images/529273888190906368/H4MJRift.jpeg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ],
              "buttons": [
                  {
                      "title": "View More",
                      "type": "postback",
                      "payload": "MORE9"
                  }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)
def chart_message10(sender_id, chart):
    song1 = chart[0]
    song2 = chart[1]
    song3 = chart[2]
    song4 = chart[3]

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
          "recipient":{
            "id":sender_id
          },
          "message": {
            "attachment": {
              "type": "template",
              "payload": {
                "template_type": "list",
                "top_element_style": "compact",
                "elements": [
                    {
                      "title": song1[0],
                      "subtitle": song1[1],
                      "image_url": "https://yankeesroom.com/wp-content/uploads/2014/02/7_37_400.jpg",
                      "buttons": [
                        {
                          "title": "Lyrics",
                          "type": "postback",
                          "payload": str(song1[1] + '-' + song1[0])
                        }
                      ]
                    },
                    {
                        "title": song2[0],
                        "subtitle": song2[1],
                        "image_url": "http://www.drodd.com/images16/38-12.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song2[1] + '-' + song2[0])
                            }
                        ]
                    },
                    {
                        "title": song3[0],
                        "subtitle": song3[1],
                        "image_url": "http://fastdecals.com/shop/images/detailed/12/39_OUTLINE_nascar.jpg?t=1434622832",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song3[1] + '-' + song3[0])
                            }
                        ]
                    },
                    {
                        "title": song4[0],
                        "subtitle": song4[1],
                        "image_url": "https://joemull.com/wp-content/uploads/2017/02/40-8.jpg",
                        "buttons": [
                            {
                                "title": "Lyrics",
                                "type": "postback",
                                "payload": str(song4[1] + '-' + song4[0])
                            }
                        ]
                    }
                ]
              }
            }
          }
        })
    r = requests.post("https://graph.facebook.com/me/messages", params=params, headers=headers, data=data)

# log
def log(message):  # simple wrapper for logging to stdout on heroku
    print(str(message))
    sys.stdout.flush()

# run app
if __name__ == '__main__':
    app.run(debug=True)

# keywords - answers
def keyword(sentence):

    # keywords to catch the greeting keyword
    KWD = [["hi", "hello", "hey", "greeting", "yo"],
           ["Check, check. What's up!", "Hello, what's up.", "Hi!", "Good day."],
           ["thanks", "thank"],
           ["Then go press LIKE!!", "No, don't thank me. I'm just programmed to do this.", "Yeap.", "No problem."],
           ["bye", "adios"],
           ["Come back.", "Adios.", "Come back later.", "You enjoyed? Come back later."],
           ["dumb", "fuck", "ass", "shut", "bloody", "damn", "shit"],
           ["STOP!", "Plz... stop.", "I'm hurt.", "Seriously?"],
           ["ok", "sure", "great", "good", "okay", "fine", "nice"],
           ["Great!", "Nice!", "Yeah, yeah."],
           ["안녕", "안녕하세요", "ㅎㅇ", "하이", "헬로우", "반가워", "반갑습니다"],
           ["안녕하세요, 저는 LyricBot입니다!", "예압, 반가워요~ 저는 LyricBot입니다!"],
           ["stop", "finish", "end"],
           ["I'm sorry.", "Stopped.", "Give me another chance."]]

    sent = sentence.split()

    # catch keyword
    for word in sent:
        for x in range(len(KWD)):
            if word.lower() in KWD[x]:
                return random.choice(KWD[x + 1])
        if word.lower() == "help" or "who are you" in word.lower():
            return "Hi! I'm LyricBot. I'm here to help you find lyrics. What lyric do you want to know?"

# lyric search
def get_lyrics(query):
    if '-' not in query:
        return "How to search?" \
               "\njust type: (artist) - (song)" \
               "\nex) kendrick lamar - i"

    artist, song = query.split('-')

    if 'feat.' in artist:
        artist = artist.split('feat')[0]
    try:
        lyric = lyricwikia.get_lyrics(artist, song)
        return lyric
    except:
        return 0

# music chart
def chart_search(num):
    apikey_musixmatch = '4135210e4feff8ddd282922f520588d5'
    apiurl_musixmatch = 'http://api.musixmatch.com/ws/1.1/'
    while True:
            querystring = apiurl_musixmatch + "chart.tracks.get?page=" + str(num) + "&page_size=4" + "&apikey=" + apikey_musixmatch + "&format=json" + "&f_has_lyrics=1"
            #matcher.lyrics.get?q_track=sexy%20and%20i%20know%20it&q_artist=lmfao
            request = urllib.request.Request(querystring)
            #request.add_header("Authorization", "Bearer " + client_access_token)
            request.add_header("User-Agent", "curl/7.9.8 (i686-pc-linux-gnu) libcurl 7.9.8 (OpenSSL 0.9.6b) (ipv6 enabled)" + apikey_musixmatch) #Must include user agent of some sort, otherwise 403 returned
            while True:
                try:
                    response = urllib.request.urlopen(request, timeout=4) #timeout set to 4 seconds; automatically retries if times out
                    raw = response.read()
                except socket.timeout:
                    print("Timeout raised and caught")
                    continue
                break
            json_obj = json.loads(raw.decode('utf-8'))
            body = json_obj["message"]["body"]["track_list"]
            result = []
            for track in body:
                result.append([track["track"]["track_name"], track["track"]["artist_name"], track["track"]["track_id"]])
            return result
