#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Historical Ground Truth Generator v2 - All 3 Scenes
====================================================
Each round = 3 months (1 quarter). Each round has a dominant issue.
Each country's following is based on its position on THAT issue.
Following != Alliance: following is issue-specific leadership preference.

Scenes:
  1: Pre-WWI Europe (1913Q1-1925Q2), 19 countries, 50 rounds
  2: Pre-WWII Europe (1938Q1-1950Q2), 28 countries, 50 rounds
  3: Pre-Cold War Europe (1946Q1-1958Q2), 25 countries, 50 rounds

Usage: python data/history/generate_history_v2.py
"""

import json, os
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

D="Diplomatic"; E="Economic"; M="Military"; I="Information"

def F(gp, *args):
    """Build following dict. gp=set of great power indices. Returns {idx: leader_idx or None}."""
    result = {}
    for idx in gp: result[idx] = None
    i = 0
    while i < len(args):
        cidx = args[i]
        if isinstance(cidx, int) and i+1 < len(args) and isinstance(args[i+1], (int, type(None))):
            result[cidx] = args[i+1]; i += 2
        else: i += 1
    return result

def A(*args):
    """Build actions dict. Returns {idx: (primary, secondary)}."""
    result = {}
    i = 0
    while i < len(args):
        cidx = args[i]
        if isinstance(cidx, int) and i+1 < len(args) and isinstance(args[i+1], tuple):
            result[cidx] = args[i+1]; i += 2
        else: i += 1
    return result

def qlabel(rn, base_year):
    return f"{base_year + (rn-1)//4}Q{(rn-1)%4+1}"

# =============================================================================
# SCENE 1: Pre-WWI Europe (1913-1925), 19 countries
# =============================================================================
SCENE1 = {
    "scene_id":1, "scene_name":"一战前欧洲(1913)", "base_year":1913, "num_countries":19,
    "gp":{1,2,3},
    "countries":[
        {"index":1,"name":"Germany","code":"GMY"},{"index":2,"name":"Russia","code":"RUS"},
        {"index":3,"name":"UK","code":"UKG"},{"index":4,"name":"France","code":"FRN"},
        {"index":5,"name":"Austria-Hungary","code":"AUH"},{"index":6,"name":"Italy","code":"ITA"},
        {"index":7,"name":"Ottoman Empire","code":"TUR"},{"index":8,"name":"Bulgaria","code":"BUL"},
        {"index":9,"name":"Spain","code":"SPN"},{"index":10,"name":"Belgium","code":"BEL"},
        {"index":11,"name":"Greece","code":"GRC"},{"index":12,"name":"Sweden","code":"SWD"},
        {"index":13,"name":"Netherlands","code":"NTH"},{"index":14,"name":"Romania","code":"ROM"},
        {"index":15,"name":"Portugal","code":"POR"},{"index":16,"name":"Denmark","code":"DEN"},
        {"index":17,"name":"Switzerland","code":"SWZ"},{"index":18,"name":"Serbia","code":"YUG"},
        {"index":19,"name":"Norway","code":"NOR"},
    ],
    "default_f": {4:3,5:1,6:3,7:1,8:1,9:3,10:3,11:2,12:3,13:3,14:2,15:3,16:3,17:3,18:2,19:3},
    "default_a": {1:(I,M),2:(M,D),3:(D,M),4:(D,M),5:(M,D),6:(M,D),7:(M,D),8:(M,D),
                  9:(D,E),10:(D,E),11:(M,D),12:(D,E),13:(D,E),14:(M,D),15:(D,M),
                  16:(D,E),17:(D,E),18:(M,D),19:(D,E)},
    "per_round": [
        # (round, issue_desc, f_overrides, a_overrides)
        # R1: 1913Q1
        (1,"London Conference - Balkan territorial settlement, UK leads diplomacy",
         (4,3,6,3,7,1,8,None,11,3,14,3,18,3), (3,(D,I),7,(D,M),11,(D,I),18,(D,I))),
        (2,"Second Balkan War - Bulgaria vs Serbia/Greece, Russia backs Slavic alliance",
         (8,None,11,2,14,2,18,2), (2,(M,D),8,(M,D),11,(M,D),14,(M,D),18,(M,D))),
        (3,"Treaty of Bucharest - Balkan territorial resettlement, A-H vs Russia for influence",
         (5,1,7,1,8,1,11,2,14,2,18,2), (5,(D,M),8,(D,E),11,(D,E),14,(D,E),18,(D,M))),
        (4,"Liman von Sanders crisis - German military mission to Ottoman, Russia-Germany tension",
         (7,1,18,2), (1,(M,I),2,(D,I),7,(M,D))),
        (5,"Anglo-German naval race peaks - UK dominates maritime order, Germany accelerates shipbuilding",
         (), (1,(M,I),3,(M,D))),
        (6,"Colonial competition & alliance consolidation - Franco-Russian alliance strengthens",
         (4,3,6,3), (1,(I,M),3,(D,M),4,(M,D))),
        (7,"July Crisis - diplomatic crisis management, states choose between war and peace",
         (4,2,5,1,6,None,7,1,8,1,10,3,11,2,14,2,18,2),
         (1,(D,I),2,(D,M),3,(D,I),4,(D,M),5,(D,M),6,(D,I),18,(D,M))),
        (8,"WWI outbreak - mobilization and initial battles, alliance camps coordinate militarily",
         (4,3,5,1,6,None,7,1,8,1,10,3,11,2,14,None,18,2),
         (1,(M,D),2,(M,D),3,(M,D),4,(M,D),5,(M,D),10,(M,D),18,(M,D))),
        (9,"Ottoman enters war & Gallipoli - Entente vs Central Powers camps solidify",
         (4,3,5,1,6,None,7,1,8,1,10,3,11,3,18,2),
         (1,(M,D),3,(M,D),7,(M,D),8,(M,D))),
        (10,"Italy joins Entente (Treaty of London) - Italy now follows UK on war strategy",
         (4,3,5,1,6,3,7,1,8,1,10,3,11,3,18,2),
         (3,(M,D),6,(M,D),7,(M,D),11,(D,M))),
        (11,"Eastern Front crisis - Russian Great Retreat, Serbia overrun",
         (4,3,5,1,6,3,7,1,8,1,10,3,11,3,14,None,18,2),
         (2,(M,D),5,(M,D),8,(M,D),18,(M,D))),
        (12,"Serbia falls - Bulgaria joins Central Powers, Entente lands at Salonika",
         (4,3,5,1,6,3,7,1,8,1,10,3,11,3,18,3),
         (3,(M,D),5,(M,D),8,(M,D),11,(M,D),18,(M,D))),
        (13,"Battle of Verdun begins - Western Front war of attrition",
         (4,3,5,1,6,3,7,1,8,1,10,3,11,3,12,3,13,3,16,3,19,3),
         (1,(M,D),3,(M,D),4,(M,D),5,(M,D),6,(M,D))),
        (14,"Battle of Jutland & Portugal enters war - UK maintains naval supremacy",
         (4,3,5,1,6,3,7,1,15,3), (1,(M,D),3,(M,D),15,(M,D))),
        (15,"Somme & Brusilov Offensive - simultaneous major offensives, Romania joins Entente",
         (4,3,5,1,6,3,7,1,14,3,18,3), (1,(M,D),2,(M,D),3,(M,D),4,(M,D),14,(M,D))),
        (16,"Romania defeated & Franz Joseph dies - war fatigue emerges",
         (4,3,5,1,14,3), (1,(M,D),3,(M,D),14,(D,M))),
        (17,"Russian Revolution (Feb) & US enters war - international landscape transforms",
         (4,3,5,1,6,3,7,1,9,3,10,3,12,3,13,3,16,3,19,3),
         (1,(M,D),2,(D,I),3,(M,D))),
        (18,"French army mutinies & Greece joins Entente - Entente internal coordination strengthens",
         (4,3,5,1,6,3,7,1,11,3,14,3,18,3), (3,(M,D),11,(M,D))),
        (19,"Russian October Revolution & Caporetto - Eastern Front collapses, Italy needs UK/France support",
         (4,3,5,1,6,3,7,1,11,3,14,3,18,3), (1,(M,D),2,(D,I),3,(M,D),6,(M,D))),
        (20,"Passchendaele & Cambrai - new technology warfare (tanks, aircraft)",
         (4,3,5,1,6,3,7,1,10,3,11,3,14,3,15,3,18,3), (1,(M,D),3,(M,I))),
        (21,"Brest-Litovsk Treaty & German Spring Offensive preparations - Russia exits, Germany masses west",
         (4,3,5,1,6,3,9,3,10,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3),
         (1,(M,D),3,(M,D),4,(M,D))),
        (22,"German Spring Offensive & Allied unified command (Foch) - A-H/Ottoman/Bulgaria wavering",
         (4,3,5,1,6,3,7,None,8,None,10,3,11,3,14,3,18,3),
         (1,(M,D),3,(M,D),5,(M,D),7,(M,D))),
        (23,"Hundred Days Offensive & Central Powers collapse - Bulgaria & Ottoman surrender",
         (4,3,5,None,6,3,7,None,8,None,10,3,11,3,14,3,18,3),
         (3,(M,D),5,(D,M),7,(D,M),8,(D,M))),
        (24,"Armistice - WWI ends, empires dissolve, UK dominates postwar order",
         (4,3,5,None,6,3,7,None,8,None,9,3,10,3,12,3,13,3,16,3,17,3,19,3),
         (1,(D,E),3,(D,E))),
        (25,"Paris Peace Conference opens - UK dominates postwar settlement, Wilson's Fourteen Points",
         (4,3,5,None,6,3,7,None,8,None,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3),
         (1,(D,E),3,(D,E),4,(D,M))),
        (26,"Treaty of Versailles signed - Germany accepts war guilt and reparations",
         (4,3,5,None,6,3,7,None,8,None,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3),
         (3,(D,E),4,(D,E),1,(D,E))),
        (27,"Treaty of Saint-Germain - Austria-Hungary formally dissolved, Central Europe redrawn",
         (4,3,9,3,10,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3), (3,(D,E))),
        (28,"Treaty of Neuilly & Greco-Turkish War begins - Bulgaria loses territory",
         (7,None,8,None,11,3,14,3,18,3), (3,(D,E),11,(M,D),7,(M,D))),
        (29,"League of Nations founded - UK leads collective security mechanism",
         (4,3,6,3,9,3,10,3,11,3,12,3,13,3,14,3,15,3,16,3,17,3,18,3,19,3),
         (3,(D,E),6,(D,E),9,(D,E))),
        (30,"Treaty of Trianon & Little Entente - Central European order established, France leads Little Entente",
         (4,3,6,3,14,3,18,3), (3,(D,E),4,(M,D))),
        (31,"Polish-Soviet War - Red Army threatens Central Europe, West aids Poland",
         (4,3,6,3,9,3,10,3,12,3,13,3,14,3,16,3,17,3,18,3,19,3), (2,(M,D))),
        (32,"Greco-Turkish War intensifies & Treaty of Sevres - Ottoman Empire partitioned",
         (7,None,11,3,18,3), (3,(D,E),7,(M,D),11,(M,D))),
        (33,"Reparations negotiations - London conference sets German reparations total, France demands harsh terms",
         (4,3,6,3,12,3,13,3,16,3,17,3,19,3), (1,(E,D),3,(E,D),4,(D,E))),
        (34,"Anglo-Soviet Trade Agreement - UK leads economic engagement with Soviet Russia",
         (4,3,6,3,12,3,13,3,16,3,19,3), (2,(E,D),3,(E,D))),
        (35,"Washington Naval Conference preparations & Austrian economic dependence on Germany",
         (4,3,5,1,6,3,12,3,13,3,16,3,19,3), (3,(D,E),1,(E,D))),
        (36,"Washington Naval Treaty - naval disarmament (5-power treaty)",
         (4,3,6,3,9,3,10,3,12,3,13,3,16,3,19,3), (3,(D,E),1,(D,E))),
        (37,"Genoa Conference - European economic reconstruction, Soviet Russia invited",
         (4,3,5,1,6,3,9,3,10,3,12,3,13,3,16,3,17,3,19,3), (1,(E,D),2,(E,D),3,(E,D))),
        (38,"Treaty of Rapallo - Germany-Soviet secret cooperation, Germany breaks Versailles isolation",
         (4,3,5,1,6,3,12,3,13,3,16,3,17,3,19,3), (1,(D,E),2,(D,M))),
        (39,"Chanak Crisis & Mussolini's March on Rome - UK faces Turkey alone, Italian fascist regime",
         (4,3,6,None,7,None,11,None,14,3,18,3), (3,(M,D),6,(I,D),7,(M,D))),
        (40,"Mussolini in power & Lausanne Conference - Italy turns to independent fascist foreign policy",
         (4,3,6,None,7,None,11,None,14,3,18,3), (3,(D,E),6,(D,I),7,(D,E))),
        (41,"Ruhr Crisis - France occupies Ruhr unilaterally, UK opposes French hardline policy",
         (4,3,5,1,6,None,9,3,10,3,12,3,13,3,16,3,17,3,19,3), (1,(E,I),3,(D,E),4,(M,D))),
        (42,"German hyperinflation - economic crisis threatens European stability",
         (4,3,5,1,6,None,12,3,13,3,16,3,17,3,19,3), (1,(E,D),3,(E,D))),
        (43,"Corfu Incident - Italy bombards Greece, League of Nations crisis",
         (4,3,6,None,7,3,11,3,14,3,18,3), (3,(D,I),6,(M,I),11,(D,I))),
        (44,"Stresemann & Dawes Plan - German economic stabilization, international coordination",
         (4,3,5,3,6,None,12,3,13,3,16,3,17,3,19,3), (1,(E,D),3,(E,D))),
        (45,"Dawes Plan adopted - German reparations restructured, UK/US lead reconstruction",
         (4,3,5,3,6,None,12,3,13,3,16,3,17,3,19,3), (1,(E,D),3,(E,D))),
        (46,"Geneva Protocol - collective security mechanism strengthened",
         (4,3,5,3,6,None,9,3,10,3,12,3,13,3,14,3,16,3,17,3,18,3,19,3), (3,(D,E))),
        (47,"London Conference - final reparations settlement, French evacuate Ruhr",
         (4,3,5,3,6,None,12,3,13,3,16,3,17,3,19,3), (1,(E,D),3,(E,D),4,(D,E))),
        (48,"Locarno preparations - Franco-German rapprochement, UK guarantees Western borders",
         (4,3,5,3,6,None,9,3,10,3,12,3,13,3,14,3,16,3,17,3,18,3,19,3), (1,(D,E),3,(D,E))),
        (49,"Locarno negotiations - Germany accepts Western borders, European reconciliation",
         (4,3,5,3,6,None,9,3,10,3,12,3,13,3,14,3,16,3,17,3,18,3,19,3), (1,(D,E),3,(D,E))),
        (50,"Locarno Treaties signed - European collective security system established",
         (4,3,5,3,6,None,9,3,10,3,12,3,13,3,14,3,16,3,17,3,18,3,19,3), (1,(D,E),3,(D,E))),
    ],
    "key_cases": {
        "France(4)":"Ally=Russia(2), follows UK(3) on naval/colonial issues. July Crisis(R7) temporarily follows Russia on security.",
        "Italy(6)":"Triple Alliance member with Germany(1), follows UK(3) on colonial/naval issues - classic issue-based defection.",
        "Netherlands(13)":"Economic ties to Germany(1), follows UK(3) on sea power/trade issues.",
        "Switzerland(17)":"German-speaking economic ties to Germany(1), follows UK(3) on security balance issues.",
    },
}

# =============================================================================
# SCENE 2: Pre-WWII Europe (1938-1950), 28 countries
# =============================================================================
SCENE2 = {
    "scene_id":2, "scene_name":"二战前欧洲(1938)", "base_year":1938, "num_countries":28,
    "gp":{1,2,3},
    "countries":[
        {"index":1,"name":"Russia","code":"RUS"},{"index":2,"name":"Germany","code":"GMY"},
        {"index":3,"name":"UK","code":"UKG"},{"index":4,"name":"France","code":"FRN"},
        {"index":5,"name":"Italy","code":"ITA"},{"index":6,"name":"Poland","code":"POL"},
        {"index":7,"name":"Spain","code":"SPN"},{"index":8,"name":"Czechoslovakia","code":"CZE"},
        {"index":9,"name":"Belgium","code":"BEL"},{"index":10,"name":"Romania","code":"ROM"},
        {"index":11,"name":"Turkey","code":"TUR"},{"index":12,"name":"Yugoslavia","code":"YUG"},
        {"index":13,"name":"Sweden","code":"SWD"},{"index":14,"name":"Netherlands","code":"NTH"},
        {"index":15,"name":"Hungary","code":"HUN"},{"index":16,"name":"Greece","code":"GRC"},
        {"index":17,"name":"Portugal","code":"POR"},{"index":18,"name":"Luxembourg","code":"LUX"},
        {"index":19,"name":"Denmark","code":"DEN"},{"index":20,"name":"Finland","code":"FIN"},
        {"index":21,"name":"Switzerland","code":"SWZ"},{"index":22,"name":"Bulgaria","code":"BUL"},
        {"index":23,"name":"Norway","code":"NOR"},{"index":24,"name":"Latvia","code":"LAT"},
        {"index":25,"name":"Lithuania","code":"LIT"},{"index":26,"name":"Ireland","code":"IRE"},
        {"index":27,"name":"Estonia","code":"EST"},{"index":28,"name":"Albania","code":"ALB"},
    ],
    "default_f": {4:3,5:2,6:3,7:None,8:3,9:3,10:3,11:3,12:3,13:3,14:3,15:2,16:3,
                  17:None,18:3,19:3,20:None,21:3,22:2,23:3,24:None,25:None,26:None,27:None,28:5},
    "default_a": {1:(D,M),2:(D,I),3:(D,I),4:(D,M),5:(M,D),6:(D,M),7:(M,D),8:(D,I),
                  9:(D,E),10:(D,M),11:(D,E),12:(D,M),13:(D,E),14:(D,E),15:(D,I),
                  16:(D,E),17:(D,E),18:(D,E),19:(D,E),20:(D,M),21:(D,E),22:(D,M),
                  23:(D,E),24:(D,E),25:(D,E),26:(D,E),27:(D,E),28:(D,E)},
    "per_round": [
        # R1: 1938Q1 - Anschluss preparation, Germany pressures Austria
        (1,"Pre-Anschluss tensions - Germany pressures Austria, UK/France appeasement posture",
         (4,3,5,2,6,3,7,None,8,3,9,3,10,3,12,3,13,3,14,3,15,2,16,3,17,None,20,None,22,2,23,3),
         (2,(D,I),3,(D,I),4,(D,I),5,(D,M),8,(D,I))),
        # R2: 1938Q2 - Anschluss (Germany annexes Austria), Sudeten crisis brewing
        (2,"Anschluss - Germany annexes Austria, Sudeten crisis begins, appeasement continues",
         (4,3,5,2,6,3,8,3,9,3,10,3,12,3,14,3,15,2,16,3,20,None,22,2,23,3),
         (2,(M,I),3,(D,I),4,(D,I),5,(D,M),8,(D,I))),
        # R3: 1938Q3 - Sudeten Crisis peaks, war appears imminent
        (3,"Sudeten Crisis peaks - Germany demands Sudetenland, Europe on brink of war, UK mediates",
         (4,3,5,2,6,3,8,3,9,3,10,3,12,3,13,3,14,3,15,2,16,3,20,None,22,2,23,3),
         (2,(D,I),3,(D,I),4,(D,I),8,(D,I))),
        # R4: 1938Q4 - Munich Agreement, Czechoslovakia abandoned
        (4,"Munich Agreement - UK/France sacrifice Czechoslovakia to Germany, appeasement peak",
         (8,None,4,3,6,3,10,3,12,3,14,3,15,2,16,3,20,None,22,2,23,3),
         (2,(D,I),3,(D,I),4,(D,I),8,(D,I))),
        # R5: 1939Q1 - Germany occupies Prague (rest of Czechoslovakia)
        (5,"Germany occupies Prague - appeasement ends, UK/France guarantee Poland and Romania",
         (6,3,8,None,10,3,12,3,14,3,15,2,16,3,20,None,22,2,23,3),
         (2,(M,I),3,(D,I),4,(D,M),8,(M,D))),
        # R6: 1939Q2 - Anglo-Polish military alliance, Molotov-Ribbentrop negotiations
        (6,"Anglo-Polish alliance & Nazi-Soviet negotiations - Europe polarizes",
         (6,3,8,None,10,3,15,2,24,None,25,None,27,None,20,3),
         (3,(D,I),6,(D,M),2,(I,M),1,(D,M))),
        # R7: 1939Q3 - Molotov-Ribbentrop Pact, Germany invades Poland, WWII begins
        (7,"WWII begins - Germany invades Poland, UK/France declare war, USSR occupies eastern Poland",
         (6,3,8,None,9,3,14,3,10,3,20,3,24,1,25,1,27,1,1,None),
         (2,(M,I),6,(M,D),3,(M,D),4,(M,D),1,(M,D),9,(M,D),14,(D,E))),
        # R8: 1939Q4 - Poland falls, Winter War (USSR vs Finland), Phoney War in West
        (8,"Poland falls & Winter War begins - Finland resists USSR, Phoney War in the West",
         (6,3,10,3,20,3,24,1,25,1,27,1,13,3,23,3,19,3),
         (2,(M,D),6,(D,M),3,(D,M),4,(D,M),1,(M,D),20,(M,D))),
        # R9: 1940Q1 - Winter War ends (Finland cedes territory), Phoney War continues
        (9,"Winter War ends - Finland cedes territory to USSR, Phoney War in West continues",
         (6,3,10,3,20,1,24,1,25,1,27,1,13,3,23,3,19,3,9,3),
         (3,(D,M),1,(M,D),20,(D,M),4,(D,M))),
        # R10: 1940Q2 - Blitzkrieg in West: Denmark, Norway, Belgium, Netherlands, Luxembourg fall
        (10,"Germany blitzkrieg through Western Europe - Denmark/Norway/Belgium/Netherlands fall",
         (19,None,23,None,9,None,14,None,18,None,4,3,10,3,6,3,12,3,13,3,16,3,17,None),
         (2,(M,I),19,(M,D),23,(M,D),9,(M,D),14,(M,D),18,(M,D),4,(M,D),3,(M,D))),
        # R11: 1940Q3 - France falls, Vichy regime, Battle of Britain, Italy joins Axis
        (11,"France surrenders & Battle of Britain - Vichy France, Italy joins war on German side, UK stands alone",
         (4,None,5,2,9,None,14,None,18,None,19,None,23,None,10,3,6,3,12,3,16,3),
         (2,(M,I),4,(D,M),3,(M,D),5,(M,D))),
        # R12: 1940Q4 - Hungary/Romania/Bulgaria join Axis, Greece resists Italy
        (12,"Axis expands - Hungary/Romania/Bulgaria join Axis, Greece resists Italian invasion",
         (15,2,22,2,10,2,4,None,16,3,12,3,6,3,17,None,11,3),
         (3,(M,D),2,(D,M),15,(M,D),22,(D,M),10,(D,M),16,(M,D))),
        # R13: 1941Q1 - Yugoslav coup (anti-Axis), Lend-Lease begins
        (13,"Yugoslav coup against Axis & Lend-Lease begins - UK gains ally, US supports UK materially",
         (12,3,10,2,22,2,15,2,16,3,6,3,17,None,11,3),
         (2,(M,D),12,(D,M),15,(M,D),22,(M,D),10,(M,D))),
        # R14: 1941Q2 - Germany invades Yugoslavia/Greece, both occupied
        (14,"Germany invades Yugoslavia & Greece - Balkans fall to Axis, Crete airborne invasion",
         (12,None,16,None,10,2,22,2,15,2,6,3,11,3),
         (2,(M,I),12,(M,D),16,(M,D),3,(M,D))),
        # R15: 1941Q3 - Operation Barbarossa begins, USSR joins Allies
        (15,"Barbarossa begins - Germany invades USSR, USSR joins Allies, Eastern Front opens",
         (1,3,6,3,12,None,16,None,10,2,22,2,15,2,20,3),
         (2,(M,I),1,(M,D),3,(D,M))),
        # R16: 1941Q4 - Battle of Moscow, Pearl Harbor, US enters war
        (16,"Battle of Moscow & Pearl Harbor - USSR holds at Moscow, US enters war, global coalition forms",
         (1,3,6,3,20,3,10,2,22,2,15,2,17,3,11,3),
         (2,(M,D),1,(M,D),3,(M,D),4,(M,D))),
        # R17-21: 1942-1943 - Total war, Allies coordinate, Axis at peak then turning points
        (17,"Total war - Stalingrad, El Alamein, Midway; Axis at peak, Allies build offensive capacity",
         (1,3,4,3,5,2,6,3,10,2,15,2,22,2,20,3,17,3,11,3,12,3,13,3,16,3),
         (1,(M,D),2,(M,D),3,(M,D),5,(M,D),11,(D,M),13,(D,E),17,(D,E),21,(D,E),26,(D,E))),
        (18,"Stalingrad turning point - German 6th Army encircled, Allies land in North Africa",
         (1,3,4,3,5,2,6,3,10,2,15,2,22,2,20,3,17,3,11,3,12,3,13,3,16,3),
         (1,(M,D),2,(M,D),3,(M,D),5,(M,D))),
        (19,"Stalingrad surrender & Kursk preparation - Axis strategic initiative lost",
         (1,3,4,3,6,3,10,2,15,2,22,2,20,3,17,3,11,3,12,3,13,3,16,3),
         (1,(M,D),2,(M,D),3,(M,D))),
        (20,"Battle of Kursk & Allied invasion of Sicily - last German Eastern offensive fails",
         (1,3,4,3,6,3,10,2,15,2,22,2,20,3,17,3,11,3,12,3,16,3),
         (1,(M,D),2,(M,D),3,(M,D),5,(M,D))),
        (21,"Italy surrenders & Allied invasion of Italy - Italian armistice, German occupation of northern Italy",
         (5,3,1,3,4,3,6,3,10,2,15,2,22,2,20,3,17,3,11,3,12,3,13,3,16,3),
         (5,(D,M),1,(M,D),2,(M,D),3,(M,D))),
        # R22: 1944Q1 - Leningrad siege lifted, Allied advance in Italy stalls
        (22,"Leningrad liberated & Italian campaign - USSR advances, Allies stuck at Monte Cassino",
         (1,3,5,3,4,3,6,3,10,2,15,2,22,2,20,3,17,3,11,3,12,3,16,3),
         (1,(M,D),2,(M,D),3,(M,D))),
        # R23: 1944Q2 - D-Day, Operation Bagration, Rome liberated
        (23,"D-Day & Operation Bagration - Allies land in Normandy, USSR destroys Army Group Centre",
         (1,3,4,3,5,3,6,3,10,2,15,2,22,2,20,3,9,3,14,3,18,3,16,3),
         (1,(M,D),2,(M,D),3,(M,D),4,(M,D))),
        # R24: 1944Q3 - Romania switches sides, Warsaw Uprising, Allies liberate France
        (24,"Romania switches sides & Warsaw Uprising - Eastern Europe in flux, Allies liberate France and Belgium",
         (10,1,22,1,20,1,4,3,5,3,6,1,9,3,14,3,18,3,15,2,12,3,16,3),
         (10,(M,D),22,(D,M),20,(M,D),1,(M,D),3,(M,D),4,(M,D))),
        # R25: 1944Q4 - Battle of the Bulge, Hungary under German occupation
        (25,"Battle of the Bulge & Soviet advance into Hungary - Germany's last Western offensive fails",
         (10,1,22,1,15,2,4,3,5,3,6,1,9,3,14,3,18,3),
         (1,(M,D),2,(M,D),3,(M,D),4,(M,D))),
        # R26: 1945Q1 - Yalta Conference, Soviet advance to Berlin, Allies cross Rhine
        (26,"Yalta Conference & race to Berlin - postwar order planned, Allied offensive in West and East",
         (10,1,22,1,15,2,20,1,4,3,5,3,6,1,9,3,14,3,18,3),
         (1,(M,D),2,(M,D),3,(D,M),4,(M,D))),
        # R27: 1945Q2 - Germany surrenders, VE Day, Potsdam preparations
        (27,"Germany surrenders - VE Day, postwar occupation zones, Potsdam Conference preparation",
         (2,None,4,3,5,3,6,1,10,1,22,1,15,2,20,1,24,1,25,1,27,1,8,1,9,3,14,3),
         (1,(D,M),2,(D,M),3,(D,M),4,(D,M))),
        # R28: 1945Q3 - Potsdam Conference, atomic bombs, Japan surrenders
        (28,"Potsdam Conference & end of WWII - atomic bombs, Japan surrenders, Cold War seeds planted",
         (2,None,4,3,5,3,6,1,10,1,22,1,20,1,24,1,25,1,27,1,8,1,9,3,14,3,23,3,19,3),
         (1,(D,M),2,(D,M),3,(D,M))),
        # R29: 1945Q4 - Postwar order established: USSR dominates East, UK dominates West
        (29,"Postwar order crystallizes - Soviet sphere in Eastern Europe, UK leads Western Europe",
         (4,3,5,3,6,1,8,1,9,3,10,1,12,1,14,3,15,1,17,3,18,3,19,3,20,1,22,1,23,3,24,1,25,1,27,1,28,1),
         (1,(D,M),3,(D,M),4,(D,M))),
        # R30: 1946Q1 - Iron Curtain speech, Greek Civil War begins
        (30,"Churchill's Iron Curtain speech & Greek Civil War begins - Cold War rhetoric escalates",
         (4,3,5,3,6,1,8,1,9,3,10,1,12,1,14,3,15,1,16,3,17,3,18,3,19,3,20,1,22,1,23,3,24,1,25,1,27,1,28,1),
         (1,(D,M),3,(D,M),16,(M,D))),
        # R31: 1946Q2 - Paris Peace Treaties negotiations, Turkey crisis (Soviet demands)
        (31,"Paris Peace Treaties & Turkey crisis - USSR demands Turkish Straits, West resists",
         (4,3,5,3,6,1,8,1,9,3,10,1,12,1,14,3,15,1,16,3,11,3,17,3,18,3,19,3,20,1,22,1,23,3,24,1,25,1,27,1,28,1),
         (1,(D,M),2,(M,D),3,(D,M),11,(D,M))),
        # R32: 1946Q3 - Truman Doctrine preparation, Bulgarian monarchy abolished
        (32,"Cold War polarization accelerates - Bulgaria becomes People's Republic, West consolidates",
         (6,1,8,1,10,1,12,1,15,1,20,1,22,1,24,1,25,1,27,1,28,1,4,3,5,3,9,3,14,3,16,3,17,3,18,3,19,3,23,3),
         (1,(D,M),3,(D,M))),
        # R33-R40: 1947-1949 - Truman Doctrine, Marshall Plan, Berlin Blockade, NATO
        (33,"Truman Doctrine & Marshall Plan - US/UK lead Western economic recovery, USSR rejects, Cold War institutionalized",
         (6,1,8,1,10,1,12,1,15,1,20,1,22,1,24,1,25,1,27,1,28,1,4,3,5,3,9,3,11,3,14,3,16,3,17,3,18,3,19,3,23,3,7,None,26,None),
         (1,(D,M),3,(D,M),7,(D,E),8,(D,E))),
        (34,"Czechoslovak coup - Communists take power in Czechoslovakia, West alarmed",
         (8,1,6,1,10,1,12,1,15,1,20,1,22,1,4,3,5,3,9,3,14,3,16,3,17,3,19,3,23,3),
         (1,(D,M),8,(D,M),2,(D,I))),
        (35,"Tito-Stalin split - Yugoslavia breaks from Soviet bloc, asserts independent communist path",
         (12,None,8,1,6,1,10,1,15,1,20,1,22,1,4,3,5,3,9,3,14,3,16,3,17,3,19,3,23,3),
         (1,(D,I),12,(D,I),2,(D,M))),
        (36,"Berlin Blockade begins - USSR blocks West Berlin, Allies organize airlift",
         (4,3,5,3,9,3,14,3,19,3,23,3,17,3,8,1,6,1,10,1,15,1,20,1,22,1),
         (1,(M,I),2,(M,D),3,(M,D),4,(M,D))),
        (37,"Berlin Airlift ongoing & NATO negotiations - Western allies demonstrate resolve",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,25,3,8,1,6,1,15,1,20,1,22,1),
         (1,(M,I),2,(M,D),3,(D,M))),
        (38,"NATO founded - Western collective defense alliance established",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,25,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (2,(D,M),3,(D,M),4,(D,M),9,(D,M),10,(D,M),17,(D,M),18,(D,M),19,(D,M),23,(D,M),1,(D,I))),
        (39,"Berlin Blockade ends & Soviet atomic bomb - USSR tests A-bomb, Cold War arms race begins",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,25,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(D,I),2,(D,M))),
        (40,"Two German states founded - FRG (West Germany) and GDR (East Germany) established",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,25,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(D,M),2,(D,M))),
        # R41-R50: 1950 - Korean War and Cold War intensification
        (41,"Korean War begins - North Korea invades South, Cold War turns hot in Asia, West unites behind US/UK",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,25,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1,7,None,26,None),
         (1,(M,D),3,(M,D),4,(M,D))),
        (42,"Korean War - Inchon landing, UN forces advance north, China intervention looms",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,25,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(M,D),3,(M,D))),
        (43,"China enters Korean War - UN forces retreat, Cold War tensions peak",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,25,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(M,I),3,(M,D),4,(M,D))),
        (44,"Korean War stalemate - front stabilizes near 38th parallel, armistice talks begin",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(M,D),3,(D,M))),
        (45,"Korean War armistice talks & European integration - Schuman Plan, ECSC formed",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(D,M),3,(D,E))),
        (46,"Stalin's final years - Cold War at peak tension, McCarthyism in US",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(D,M),3,(D,M))),
        (47,"Stalin dies - USSR leadership transition, Malenkov becomes Premier, Cold War thaw begins",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(D,M),3,(D,M))),
        (48,"East German uprising & Korean armistice - Soviet bloc unrest, Korean War ends",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(M,I),3,(D,I))),
        (49,"Geneva Conference - Korea and Indochina settlements, Cold War detente begins",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(D,M),3,(D,E),4,(D,E))),
        (50,"Paris Agreements & Western European Union - West Germany rearmed within NATO framework",
         (4,3,5,3,9,3,10,3,14,3,19,3,23,3,17,3,18,3,16,3,11,3,8,1,6,1,15,1,20,1,22,1),
         (1,(D,M),3,(D,M),4,(D,M))),
    ],
    "key_cases": {
        "Italy(5)":"Axis member with Germany(2), but on colonial/Mediterranean issues follows independent path. Post-1943 armistice follows UK(3).",
        "Yugoslavia(12)":"Communist state, initially follows USSR(1), breaks with Stalin in 1948 (R35) and becomes independent.",
        "Finland(20)":"Winter War seeks UK(3) support, post-1944 forced to follow USSR(1) on security, maintains Western economic ties.",
        "Spain(7)":"Franco regime remains independent (non-aligned) throughout, not following any great power.",
        "Romania(10)":"Pre-war follows UK(3)/France(4), joins Axis in 1940, switches to USSR(1) in 1944.",
        "Ireland(26)":"Neutral throughout WWII and early Cold War, independent of all great powers.",
    },
}

# =============================================================================
# SCENE 3: Pre-Cold War Europe (1946-1958), 25 countries
# =============================================================================
SCENE3 = {
    "scene_id":3, "scene_name":"冷战前欧洲(1946)", "base_year":1946, "num_countries":25,
    "gp":{1,2},  # Only 2 great powers: USSR(1) and UK(2); France(3) is middle power
    "countries":[
        {"index":1,"name":"Russia","code":"RUS"},{"index":2,"name":"UK","code":"UKG"},
        {"index":3,"name":"France","code":"FRN"},{"index":4,"name":"Italy","code":"ITA"},
        {"index":5,"name":"Poland","code":"POL"},{"index":6,"name":"Spain","code":"SPN"},
        {"index":7,"name":"Turkey","code":"TUR"},{"index":8,"name":"Czechoslovakia","code":"CZE"},
        {"index":9,"name":"Belgium","code":"BEL"},{"index":10,"name":"Netherlands","code":"NTH"},
        {"index":11,"name":"Sweden","code":"SWD"},{"index":12,"name":"Yugoslavia","code":"YUG"},
        {"index":13,"name":"Romania","code":"ROM"},{"index":14,"name":"Hungary","code":"HUN"},
        {"index":15,"name":"Greece","code":"GRC"},{"index":16,"name":"Bulgaria","code":"BUL"},
        {"index":17,"name":"Portugal","code":"POR"},{"index":18,"name":"Luxembourg","code":"LUX"},
        {"index":19,"name":"Denmark","code":"DEN"},{"index":20,"name":"Switzerland","code":"SWZ"},
        {"index":21,"name":"Norway","code":"NOR"},{"index":22,"name":"Finland","code":"FIN"},
        {"index":23,"name":"Ireland","code":"IRE"},{"index":24,"name":"Albania","code":"ALB"},
        {"index":25,"name":"Iceland","code":"ICE"},
    ],
    "default_f": {3:2,4:2,5:1,6:None,7:2,8:1,9:2,10:2,11:2,12:1,13:1,14:1,15:2,16:1,
                  17:2,18:2,19:2,20:2,21:2,22:1,23:None,24:1,25:2},
    "default_a": {1:(D,M),2:(D,M),3:(D,M),4:(D,E),5:(D,M),6:(D,E),7:(D,M),8:(D,M),
                  9:(D,E),10:(D,E),11:(D,E),12:(D,M),13:(D,M),14:(D,M),15:(M,D),
                  16:(D,M),17:(D,E),18:(D,E),19:(D,E),20:(D,E),21:(D,E),22:(D,E),
                  23:(D,E),24:(D,M),25:(D,E)},
    "per_round": [
        # 1946
        (1,"Postwar reconstruction begins - UN established, Iron Curtain not yet descended, wartime cooperation fading",
         (3,2,4,2,5,1,7,2,8,1,9,2,10,2,12,1,13,1,14,1,15,2,16,1,17,2,19,2,21,2,22,1,24,1,25,2),
         (1,(D,M),2,(D,M),3,(D,M),7,(D,M),15,(D,M))),
        (2,"Greek Civil War intensifies & Iran crisis - USSR pressures Turkey/Iran, West resists, Cold War tensions rise",
         (3,2,4,2,5,1,7,2,8,1,9,2,10,2,12,1,13,1,14,1,15,2,16,1,17,2,19,2,21,2,22,1,24,1,25,2),
         (1,(D,M),2,(D,M),15,(M,D),7,(D,M))),
        (3,"Paris Peace Conference - postwar treaties with Italy/Romania/Hungary/Bulgaria/Finland finalized",
         (3,2,4,2,5,1,7,2,8,1,9,2,10,2,12,1,13,1,14,1,15,2,16,1,17,2,19,2,21,2,22,1,24,1,25,2),
         (1,(D,M),2,(D,M),3,(D,M))),
        (4,"Bizone established (US/UK merge German occupation zones) - Western integration begins, USSR objects",
         (3,2,4,2,5,1,8,1,9,2,10,2,12,1,13,1,14,1,16,1,17,2,19,2,21,2,22,1,24,1,25,2),
         (1,(D,I),2,(D,M),3,(D,M))),
        # 1947
        (5,"Truman Doctrine announced - US pledges to support Greece/Turkey against communism, containment policy begins",
         (3,2,4,2,5,1,7,2,8,1,9,2,10,2,12,1,13,1,14,1,15,2,16,1,17,2,19,2,21,2,22,1,25,2),
         (1,(D,M),2,(D,M),7,(D,M),15,(M,D))),
        (6,"Marshall Plan announced - massive US economic aid for Europe, USSR rejects and forbids Eastern Bloc participation",
         (3,2,4,2,5,1,7,2,8,1,9,2,10,2,12,1,13,1,14,1,16,1,17,2,19,2,21,2,22,1,25,2),
         (1,(D,M),2,(D,E),3,(D,E),8,(D,E))),
        (7,"Cominform founded & Marshall Plan implemented - USSR tightens control over Eastern Bloc, Western Europe begins recovery",
         (5,1,8,1,12,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,7,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),2,(D,E),3,(D,E))),
        (8,"Communist consolidation in Eastern Europe - Poland/Romania/Bulgaria become people's republics",
         (5,1,8,1,12,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,7,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),2,(D,M))),
        # 1948
        (9,"Czechoslovak communist coup - last democratic Eastern European state falls to communism, West alarmed",
         (8,1,5,1,12,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,7,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),8,(D,M),2,(D,I))),
        (10,"Tito-Stalin split - Yugoslavia expelled from Cominform, asserts independent communist path, key following!=alliance case",
         (12,None,5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,7,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,I),12,(D,I),2,(D,M))),
        (11,"Berlin Blockade begins - USSR blocks West Berlin, Western Allies organize massive airlift",
         (3,2,4,2,9,2,10,2,19,2,21,2,17,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(M,I),2,(M,D),3,(M,D))),
        (12,"Berlin Airlift succeeds - Western resolve demonstrated, USSR unable to force West out of Berlin",
         (3,2,4,2,9,2,10,2,19,2,21,2,17,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(M,I),2,(M,D),3,(M,D))),
        # 1949
        (13,"NATO founded - Western collective defense: UK/France/Italy/Belgium/Netherlands/Luxembourg/Denmark/Norway/Iceland/Portugal",
         (3,2,4,2,7,2,9,2,10,2,15,2,17,2,18,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (2,(D,M),3,(D,M),4,(D,M),9,(D,M),10,(D,M),17,(D,M),18,(D,M),19,(D,M),21,(D,M),25,(D,M),1,(D,I))),
        (14,"Berlin Blockade ends & two German states founded - FRG and GDR established, Cold War division institutionalized",
         (3,2,4,2,7,2,9,2,10,2,15,2,17,2,18,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,M))),
        (15,"Soviet atomic bomb test - USSR acquires nuclear weapons, Cold War enters nuclear age, arms race begins",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,I),2,(D,M))),
        (16,"COMECON formalized - Soviet economic bloc consolidates, Eastern Europe integrated into Soviet economy",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(E,D),2,(D,E))),
        # 1950
        (17,"Schuman Declaration - European Coal and Steel Community proposed, Franco-German reconciliation begins",
         (3,2,4,2,9,2,10,2,15,2,17,2,18,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,E),3,(D,E))),
        (18,"Korean War begins - North Korea invades South, Cold War goes hot in Asia, NATO rearmed, Western solidarity peaks",
         (3,2,4,2,7,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(M,I),2,(M,D),3,(M,D))),
        (19,"Korean War - UN counteroffensive, Inchon landing, NATO establishes integrated command (SHAPE)",
         (3,2,4,2,7,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(M,D),2,(M,D),3,(M,D))),
        (20,"China enters Korean War - massive Chinese offensive, UN forces retreat, fear of wider war",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(M,I),2,(M,D),3,(M,D))),
        # 1951
        (21,"Korean War stalemate & European Defense Community proposed - front stabilizes, West German rearmament debated",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(M,D),2,(D,M),3,(D,M))),
        (22,"ECSC Treaty signed - European integration advances, Franco-German economic cooperation institutionalized",
         (3,2,4,2,9,2,10,2,15,2,17,2,18,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,E),3,(D,E),4,(D,E))),
        (23,"Korean War armistice talks begin - military stalemate, negotiations start at Kaesong/Panmunjom",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(M,D),2,(D,M))),
        (24,"UK tests atomic bomb - Britain becomes third nuclear power, NATO nuclear sharing debates begin",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,I),2,(D,M),3,(D,M))),
        # 1952
        (25,"NATO Lisbon Conference - ambitious conventional force goals, Greece/Turkey join NATO",
         (7,2,15,2,3,2,4,2,9,2,10,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (2,(D,M),7,(D,M),15,(D,M))),
        (26,"European Defense Community treaty signed - attempt to create European army, West Germany to contribute",
         (3,2,4,2,9,2,10,2,17,2,18,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,M),3,(D,M))),
        (27,"Stalin's final years - Cold War at peak tension, Soviet domestic repression intensifies, anti-Semitic campaigns",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),2,(D,M))),
        (28,"First hydrogen bomb tests - US tests H-bomb (Ivy Mike), USSR follows, thermonuclear age begins",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,I),2,(D,M))),
        # 1953
        (29,"Stalin dies - Malenkov becomes Soviet Premier, succession struggle begins, Cold War thaw signals",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),2,(D,M))),
        (30,"East German uprising - workers revolt in GDR, suppressed by Soviet tanks, demonstrates Soviet control fragility",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(M,I),2,(D,I))),
        (31,"Korean War armistice signed - war ends in stalemate, Cold War military confrontation in Asia de-escalates",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,M))),
        (32,"USSR tests hydrogen bomb & Khrushchev rises - Soviet nuclear parity approaches, leadership transition continues",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,I),2,(D,M))),
        # 1954
        (33,"Berlin Conference (Big Four) - attempt at German reunification fails, Cold War division persists",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,M),3,(D,M))),
        (34,"Geneva Conference on Indochina - French defeat at Dien Bien Phu, Vietnam partitioned, Geneva Accords",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,E),3,(M,D))),
        (35,"French National Assembly rejects EDC - European army plan collapses, alternative: West German NATO membership",
         (3,2,4,2,9,2,10,2,15,2,17,2,18,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,M),3,(D,M))),
        (36,"Paris Agreements - West Germany joins NATO, occupation ends, Western European Union formed",
         (3,2,4,2,9,2,10,2,15,2,17,2,18,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,M),3,(D,M))),
        # 1955
        (37,"Khrushchev consolidates power - Malenkov resigns, Khrushchev becomes dominant, peaceful coexistence policy",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),2,(D,M))),
        (38,"Warsaw Pact founded - Soviet response to West German NATO membership, Eastern Bloc military alliance formalized",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,12,None,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),5,(D,M),8,(D,M),13,(D,M),14,(D,M),16,(D,M),24,(D,M),2,(D,I))),
        (39,"Austrian State Treaty & Geneva Summit - Austria neutralized, Big Four summit, Spirit of Geneva detente",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,E),2,(D,E),3,(D,E))),
        (40,"West Germany joins NATO & USSR- Yugoslavia rapprochement - Khrushchev visits Belgrade, acknowledges Tito's path",
         (12,None,5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),2,(D,M))),
        # 1956
        (41,"Khrushchev's Secret Speech - denounces Stalin's crimes at 20th Party Congress, de-Stalinization begins, Eastern Bloc shaken",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,I),2,(D,I))),
        (42,"Polish October - Gomulka comes to power, Poland asserts limited autonomy while remaining in Warsaw Pact",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),2,(D,I),5,(D,M))),
        (43,"Hungarian Revolution - Hungary attempts to leave Warsaw Pact, crushed by Soviet invasion, Western condemnation but no intervention",
         (14,1,5,1,8,1,13,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(M,I),14,(M,D),2,(D,I),15,(M,D))),
        (44,"Suez Crisis - UK/France/Israel attack Egypt, US/USSR force withdrawal, demonstrates UK/France no longer independent great powers",
         (2,None,3,None,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,7,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,I),2,(M,I),3,(M,I),7,(D,I))),
        # 1957
        (45,"Treaty of Rome - EEC and EURATOM founded, European economic integration accelerates, Six sign (France/Italy/Benelux/West Germany)",
         (3,2,4,2,9,2,10,2,17,2,18,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,E),3,(D,E),4,(D,E),9,(D,E),10,(D,E),18,(D,E))),
        (46,"Sputnik launched - USSR launches first satellite, space race begins, Western technological confidence shaken",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(I,M),2,(D,M))),
        (47,"NATO dual-track on nuclear weapons - US deploys intermediate-range missiles in Europe, arms control debates",
         (3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,M),2,(D,M))),
        (48,"Khrushchev consolidates - Zhukov dismissed, Khrushchev becomes Premier as well as Party Secretary, Soviet leadership unified",
         (5,1,8,1,13,1,14,1,16,1,22,1,24,1,3,2,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2),
         (1,(D,M),2,(D,M))),
        # 1958
        (49,"De Gaulle returns to power - French Fifth Republic established, France asserts independent foreign policy, challenges UK/US leadership",
         (3,None,2,None,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,I),2,(D,M),3,(D,M))),
        (50,"Berlin Ultimatum begins - Khrushchev demands Western withdrawal from Berlin, second Berlin crisis, Cold War tension peaks",
         (3,None,4,2,9,2,10,2,15,2,17,2,19,2,21,2,25,2,5,1,8,1,13,1,14,1,16,1,22,1,24,1),
         (1,(D,I),2,(D,M),3,(D,M))),
    ],
    "key_cases": {
        "Yugoslavia(12)":"Communist state, initially follows USSR(1), breaks with Stalin in 1948 (R10) and becomes independent throughout remaining rounds.",
        "Finland(22)":"Forced to follow USSR(1) on security issues (Finlandization), but maintains Western economic/cultural ties and democratic system.",
        "Spain(6)":"Franco regime remains isolated, not following any major power bloc. Independent throughout.",
        "Ireland(23)":"Neutral throughout, independent of all great powers. UN member but non-aligned.",
        "France(3)":"Initially follows UK(2) in Western camp, but under De Gaulle (R49) becomes independent - key following != alliance case.",
        "Sweden(11)":"Formally neutral, but economically and culturally follows UK/Western camp. Not a NATO member but clearly Western-aligned.",
    },
}

# =============================================================================
# Generator function
# =============================================================================

def generate_scene(scene_config):
    """Generate round data for a scene from its per-round definition."""
    rounds = {}
    for entry in scene_config["per_round"]:
        rn, issue, f_args, a_args = entry
        # Build following dict: defaults from scene, overridden by f_args
        default_f = scene_config["default_f"]
        gp = scene_config["gp"]
        following = {}
        for idx in gp:
            following[idx] = None  # Great powers are always independent
        # Apply defaults for non-GP countries
        for idx in range(1, scene_config["num_countries"]+1):
            if idx not in gp:
                following[idx] = default_f.get(idx)
        # Apply overrides - but NEVER allow great powers to follow anyone
        i = 0
        while i < len(f_args):
            cidx = f_args[i]
            if isinstance(cidx, int) and i+1 < len(f_args) and isinstance(f_args[i+1], (int, type(None))):
                if cidx not in gp:  # Great powers are ALWAYS independent
                    following[cidx] = f_args[i+1]
                i += 2
            else:
                i += 1

        # Build actions dict
        default_a = scene_config["default_a"]
        actions = {}
        for idx in range(1, scene_config["num_countries"]+1):
            actions[idx] = default_a.get(idx, (D, E))
        i = 0
        while i < len(a_args):
            cidx = a_args[i]
            if isinstance(cidx, int) and i+1 < len(a_args) and isinstance(a_args[i+1], tuple):
                actions[cidx] = a_args[i+1]; i += 2
            else:
                i += 1

        rounds[str(rn)] = {
            "round": rn,
            "quarter": qlabel(rn, scene_config["base_year"]),
            "dominant_issue": issue,
            "following": {str(k): v for k, v in following.items()},
            "actions": {str(k): {"expected_primary": actions[k][0], "expected_secondary": actions[k][1]}
                       for k in actions},
        }
    return rounds


def build_scene_json(scene_config):
    rounds = generate_scene(scene_config)
    return {
        "scene_id": scene_config["scene_id"],
        "scene_name": scene_config["scene_name"],
        "description": f"{scene_config['scene_name']}, {scene_config['base_year']}Q1 to {scene_config['base_year']+12}Q2, {scene_config['num_countries']} countries, 50 rounds. Each round=3 months. Following is issue-specific leadership preference (NOT alliance).",
        "time_span": f"{scene_config['base_year']}-Q1 ~ {scene_config['base_year']+12}-Q2",
        "total_rounds": 50,
        "num_countries": scene_config["num_countries"],
        "rounds_per_year": 4,
        "countries": scene_config["countries"],
        "great_powers": list(scene_config["gp"]),
        "following_definition": "追随!=同盟: 追随是对某国在特定议题上的领导偏好, 不等同于战略同盟关系。盟友可能在经济议题上追随敌对阵营的领导者, 这是正常的外交现象。每轮的追随基于该轮最突出议题上的政策协调对象。",
        "key_issue_specific_cases": scene_config["key_cases"],
        "rounds": rounds,
    }


# =============================================================================
# Main
# =============================================================================

def main():
    scenes = [
        (SCENE1, "scene1_prewar_1913.json"),
        (SCENE2, "scene2_prewar_1938.json"),
        (SCENE3, "scene3_prewar_1946.json"),
    ]

    for config, filename in scenes:
        data = build_scene_json(config)
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        rounds = data['rounds']
        # Count per-country following changes
        from collections import defaultdict
        changes = defaultdict(int)
        for cidx in range(1, config["num_countries"]+1):
            if cidx in config["gp"]: continue
            prev = None
            for rn in range(1, 51):
                cur = rounds[str(rn)]['following'][str(cidx)]
                if cur != prev:
                    changes[cidx] += 1
                    prev = cur

        names = {c['index']: c['name'] for c in config['countries']}
        avg_changes = sum(changes.values()) / len(changes) if changes else 0

        print(f"[OK] {filename}")
        print(f"  Scene: {data['scene_name']}, {config['num_countries']} countries, 50 rounds")
        print(f"  Time: {data['time_span']}")
        print(f"  Great powers: {[names[i] for i in config['gp']]}")
        print(f"  Avg following changes per country: {avg_changes:.1f}")
        top_changers = sorted(changes.items(), key=lambda x: -x[1])[:5]
        print(f"  Most changes: {', '.join([f'{names[idx]}({c})' for idx,c in top_changers])}")
        print()

    print("All 3 scene history files generated successfully (v2).")


if __name__ == "__main__":
    main()
