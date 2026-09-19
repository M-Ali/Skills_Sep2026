---
name: auto-dealer-engine
description: "Dealer Engine of autopulse (Automotive Growth Intelligence for one Pakistan auto client at a time, e.g. Suzuki or Hyundai): answers 'where are we winning or losing' across the dealer network - the funnel from enquiries and walk-ins to test drives, bookings and sales per dealer, where the leakage is, and a peer-group benchmark of what each dealer should reasonably be selling given its catchment, stock and history. Use whenever the user mentions dealers, dealerships, 3S outlets, showroom performance, lead conversion, test drives, bookings, underperforming dealers, dealer benchmarking or ranking, dealer catchments, or shares a client's dealer, CRM or lead file - even if they only say 'which dealers are doing badly'. Client data only: never mixes two clients."
---

# Dealer Engine

**Question it answers:** where are we winning or losing?
**Data:** one client's own data (`data/clients/<client>/`), never committed,
never shown to another client. Public data may be added (population, catchment
features), never another client's.
**Project:** `D:/personal/BHT_Sep26` (uv app `autopulse`).

## Status

The **public half is built**; the private half still needs a client.

```bash
uv run autopulse dealer fetch                      # all four brands, today's snapshot
uv run autopulse dealer report --client Hyundai    # coverage, white space, changes
uv run autopulse dealer report --period 2026-09    # also writes signals
```

What came back on 18 Sep 2026: **Suzuki 204 outlets, all with coordinates the
site publishes** (170 of them car outlets, the rest motorcycles and outboard
motors); **Hyundai 27** with addresses and a Google Maps link each, no
coordinates; **Toyota 57** names, of which only 11 carry a city in the name;
**Honda refused** every request (403).

| Brand | What the page gives | Caveat |
|---|---|---|
| Suzuki | name, address, phone, email, city, area, category **and per-outlet coordinates** | the same company appears once for cars and once for motorcycles: they are separate outlets, and the id keeps them apart |
| Hyundai | city, name, phone, address, email, a Google Maps link | no coordinates; the links are stored and can be resolved later |
| Toyota | dealer names, and the city list, in booking dropdowns | which dealer sits in which city is decided by the page's JavaScript, so it is **not** read: a city is recorded only when the name carries one |
| Honda | nothing: 403 to any non-browser request | needs the browser tool |

Robots files were checked on 18 Sep 2026: Hyundai and Toyota allow these pages,
Honda blocks only PDFs, the Suzuki sites publish no robots file. Use the OEM
sites rather than PakWheels' directory, whose terms are stricter.

Against the census households already in the database this gives, with no client
data at all: outlets per 100,000 households by city, white space where a rival
has an outlet and the client doesn't, and openings and closures between
snapshots. Each fetch is stored as a dated snapshot and rows are never
overwritten, because an OEM listing is a current claim that lags closures.

**A limit found while building this:** the census workbook's district sheets are
incomplete - they cover 73% of Punjab's households, 64% of KPK's, and have no
Peshawar, Mardan or Islamabad at all. So 62 cities with outlets have no household
figure. The report says so rather than leaving a blank, and a city with no figure
is never treated as a city with no people.

The private half below - the funnel and peer benchmark - still needs a pilot
client. Say plainly that no client numbers exist until then.

## Why the client wall is structural here

The group handles Suzuki and Hyundai. Dealer data shows a client's weakest
outlets and conversion rates, which is exactly what a competitor would want.
So a run of this engine reads **one** client folder, writes signals with
`scope=client:<name>`, and peer groups contain only that client's dealers.
Comparing a Suzuki dealer with a Hyundai dealer is not allowed, even
anonymised.

## What is code and what is judgement

- **Code:** funnel rates, peer grouping, expected sales, gaps, signals.
- **Judgement:** which dealer gaps are worth an intervention, what could
  explain them (stock, location, staff, competition nearby), and how to word
  that as something to investigate.

## Data request (send to the client)

Per dealer per month, whichever exist:

| field | notes |
|---|---|
| dealer_id, dealer name, city, address or lat/lng | lat/lng lets catchments be built |
| enquiries (by source: walk-in, phone, web, social) | |
| test_drives | |
| bookings | |
| deliveries / sales (by model) | should reconcile with the client's PAMA total |
| stock on hand, days in stock (by model) | Pakistan often runs on bookings, so booking-to-delivery days may matter more than stock age |
| booking_to_delivery_days | |
| staff count, opening date | for productivity and new-dealer ramp-up |

## Method

1. **Check the file.** Months covered, dealers covered, blanks, whether
   deliveries per month sum close to the client's PAMA sales for the same
   months. List gaps; don't fill them.
2. **Funnel per dealer:** enquiry → test drive → booking → sale rates, and
   where each dealer's biggest drop is compared with the network median.
3. **Catchment features** (public): population within a drive-time or
   radius from census tables, competitor outlets nearby from OpenStreetMap
   (reuse `osm-poi` in `D:/personal/map`), city tier.
4. **Peer groups:** cluster dealers on catchment and history features (not on
   the sales being judged), then compute each dealer's expected sales as its
   peer group's median rate × its own catchment/enquiries. Gap = actual −
   expected. Report the peer group beside every gap so "underperforming" is
   always "against these similar dealers".
5. **Write signals** and a ranked list of gaps, each worded as an
   investigation.

## Signals this engine writes

`engine=dealer`, `scope=client:<name>`, `geography=<city>/<dealer_id>`.

| metric | comparisons |
|---|---|
| `enquiries`, `test_drives`, `bookings`, `sales` | level, mom, yoy |
| `conv_enquiry_to_testdrive_pct`, `conv_testdrive_to_booking_pct`, `conv_booking_to_sale_pct` | level, mom |
| `sales_vs_peer_expected_pct` | level |
| `booking_to_delivery_days` | level, mom |

Load and check with `autopulse signals check <files> --client <name>`: it
refuses any other client's rows.

## Limits

- No phone-location footfall panel is known for Pakistan; walk-ins come from
  dealer logs, which dealers may under-record. Say so.
- Fewer than ~15 dealers or ~12 months makes peer groups and expected sales
  fragile: report funnel rates only.

## Changelog

- 2026-09-18: public dealer sources checked and recorded (Suzuki, Hyundai,
  Toyota, Honda), with their robots files. Census households by district are in
  the database, so catchment work needs no client data. Still no code.
- 2026-09-17: created. Method and data request only; no data, no code.
