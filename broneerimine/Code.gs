/**
 * Leola Meestejuuksur: veebilehe broneeringud Google Sheetsi.
 *
 * Mida see teeb
 *  - Võtab veebilehe vormist broneeringu vastu ja kirjutab selle lehele „Broneeringud”.
 *  - Ütleb vormile, millised ajad on vabad. Võetud aeg kaob vormist, nii et topeltbroneeringut ei teki.
 *    Arvesse lähevad ka käsitsi lisatud read, juuksurite tööpäevad ja puudumised.
 *  - Kaitseb võltsbroneeringute eest: ainult Eesti mobiilinumbrid, kuni 2 tulevast aega ühele numbrile,
 *    blokeeritud numbrid ja automaatne paus, kui lühikese ajaga tuleb liiga palju broneeringuid.
 *
 * Paigaldamise ja kasutamise juhend on samas kaustas failis README.md.
 * Kui muudad seda koodi, avalda uus versioon: Deploy → Manage deployments → pliiats → Version: New version → Deploy.
 */

// Script pääseb ligi ainult sellele ühele tabelile, mitte sinu teistele failidele:
/** @OnlyCurrentDoc */

// --------------------------------------------------------------------------------------------- seaded

// Lahtiolekuajad, pühapäev = 0. Peavad klappima veebilehe omadega (index.html, HOURS).
const OPENING_HOURS = [null, [8, 15], [8, 17], [8, 17], [8, 17], [8, 17], [8, 15]];
// Ühe broneeringu pikkus tundides. Veebilehel on sama (SLOT).
const SLOT = 1;
// Mitu päeva ette saab netis aega võtta.
const DAYS_AHEAD = 14;
// Mitu tulevast broneeringut võib ühel telefoninumbril korraga olla.
const MAX_PER_PHONE = 2;
// Kui SPAM_MINUTES minuti jooksul on tulnud juba SPAM_COUNT broneeringut, pannakse netibroneerimine pausile.
const SPAM_COUNT = 6;
const SPAM_MINUTES = 10;
// Kuhu saata kiri, kui netibroneerimine pandi pausile. Tühi = selle Google'i konto aadress, kes scripti avaldas.
const ALERT_EMAIL = '';
const SALON_PHONE = '433 3242';
// Juuksurid, kes pannakse lehele „Juuksurid” esimesel seadistamisel. Hiljem muuda nimekirja otse tabelis.
const FIRST_STYLISTS = ['Rita', 'Maire', 'Kaire', 'Laine', 'Hele', 'Reelika'];

// ---------------------------------------------------------------------------------- tabeli ülesehitus

const TIME_ZONE = 'Europe/Tallinn';
const SHEET = {
  overview: 'Ülevaade',
  bookings: 'Broneeringud',
  stylists: 'Juuksurid',
  absences: 'Puudumised',
  blocked: 'Blokeeritud',
};
const BOOKING_HEAD = ['Kuupäev', 'Kell', 'Juuksur', 'Teenus', 'Klient', 'Telefon', 'Staatus', 'Tuli?', 'Märkus', 'Loodud'];
const COL = { date: 0, time: 1, stylist: 2, service: 3, client: 4, phone: 5, status: 6, came: 7, note: 8, created: 9 };
// Monday first, as the salon reads the week.
const STYLIST_HEAD = ['Nimi', 'Mobiil', 'E', 'T', 'K', 'N', 'R', 'L', 'P'];
const ABSENCE_HEAD = ['Juuksur', 'Alates', 'Kuni', 'Märkus'];
const BLOCKED_HEAD = ['Telefon', 'Märkus', 'Lisatud'];
const ACTIVE = 'Aktiivne';
const CANCELLED = 'Tühistatud';
const EVERYONE = 'Kõik';
const DATE_FORMAT = 'ddd dd.mm.yyyy';
const TIME_FORMAT = 'hh:mm';
const STAMP_FORMAT = 'dd.mm.yyyy hh:mm';

// -------------------------------------------------------------------------------- veebilehe pöördumised

// The form asks which hours are free. Only names and hours leave the sheet, never clients.
function doGet() {
  try {
    const state = readState_();
    return json_({ ok: true, paused: isPaused_(), stylists: state.stylists.map((s) => s.name), free: state.free });
  } catch (error) {
    console.error(error);
    return json_(fail_('server', 'Vabu aegu ei õnnestunud laadida.'));
  }
}

// The form sends a booking as JSON (as plain text, so the browser does not ask Google for permission first).
function doPost(e) {
  let data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch (error) {
    return json_(fail_('invalid', 'Broneeringut ei õnnestunud lugeda. Proovi uuesti.'));
  }
  // Only a robot fills the field people never see: answer as if all went well and keep nothing.
  if (data.website) return json_({ ok: true, stylist: clean_(data.stylist, 40), date: clean_(data.date, 10), time: clean_(data.time, 5) });
  const request = parseRequest_(data);
  if (!request.ok) return json_(request);
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return json_(fail_('busy', 'Praegu on palju broneerimisi korraga. Proovi mõne hetke pärast uuesti.'));
  try {
    return json_(book_(request));
  } catch (error) {
    console.error(error);
    return json_(fail_('server', `Saatmine ei õnnestunud. Proovi uuesti või helista ${SALON_PHONE}.`));
  } finally {
    lock.releaseLock();
  }
}

function parseRequest_(data) {
  const name = clean_(data.name, 60);
  const service = clean_(data.service, 60);
  const stylist = clean_(data.stylist, 40);
  const phone = normalizePhone_(data.phone);
  const date = clean_(data.date, 10);
  const hour = parseHour_(data.time);
  if (name.length < 2) return fail_('name', 'Kirjuta oma nimi.');
  if (!phone) return fail_('phone', 'Kirjuta Eesti mobiilinumber, näiteks 5123 4567.');
  if (!service) return fail_('invalid', 'Vali teenus.');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || hour === null) return fail_('invalid', 'Vali päev ja kellaaeg.');
  return { ok: true, name, service, stylist: /^pole vahet$/i.test(stylist) ? '' : stylist, phone, date, hour };
}

// Runs under the script lock, so two people can never take the same hour.
function book_(request) {
  if (isPaused_()) return fail_('paused', `Netibroneerimine on praegu suletud. Aja saad kinni panna telefonil ${SALON_PHONE}.`);
  const state = readState_();
  if (state.blocked.has(request.phone)) return fail_('blocked', `Selle numbriga ei saa netis aega broneerida. Helista ${SALON_PHONE}.`);

  const mine = state.upcoming.filter((b) => b.phone === request.phone);
  const same = mine.find((b) => b.date === request.date && b.hour === request.hour);
  if (same) {
    // The same booking sent twice (an answer lost on the way, a double tap) is answered as done.
    if (!request.stylist || sameName_(same.stylist, request.stylist)) return done_(same.stylist, request);
    return fail_('taken', `Sul on sel ajal juba aeg ${same.stylist} juures.`);
  }
  if (mine.length >= MAX_PER_PHONE) {
    return fail_('limit', `Sellel numbril on juba ${mine.length} aega ees. Uue aja saad kinni panna telefonil ${SALON_PHONE}.`);
  }

  const day = state.free[request.date] || {};
  const freeAt = (name) => (day[name] || []).indexOf(request.hour) !== -1;
  let stylist;
  if (request.stylist) {
    const match = state.stylists.find((s) => sameName_(s.name, request.stylist));
    if (!match) return fail_('stylist', 'Sellist juuksurit ei leitud. Vali juuksur uuesti.');
    stylist = match.name;
    if (!freeAt(stylist)) return fail_('taken', 'See aeg on vahepeal ära võetud. Vali palun uus aeg.');
  } else {
    // "Pole vahet": whoever is free then and has the fewest clients that day.
    const options = state.stylists.map((s) => s.name).filter(freeAt);
    if (!options.length) return fail_('taken', 'See aeg on vahepeal ära võetud. Vali palun uus aeg.');
    const load = (name) => state.upcoming.filter((b) => b.date === request.date && sameName_(b.stylist, name)).length;
    stylist = options.reduce((best, name) => (load(name) < load(best) ? name : best));
  }

  const props = PropertiesService.getScriptProperties();
  const since = Date.now() - SPAM_MINUTES * 60000;
  const recent = JSON.parse(props.getProperty('recent') || '[]').filter((t) => t > since);
  if (recent.length >= SPAM_COUNT) {
    props.setProperty('paused', 'auto');
    alertOwner_();
    return fail_('paused', `Netibroneerimine on praegu suletud. Aja saad kinni panna telefonil ${SALON_PHONE}.`);
  }

  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const date = Utilities.parseDate(request.date, ss.getSpreadsheetTimeZone(), 'yyyy-MM-dd');
  ss.getSheetByName(SHEET.bookings).appendRow([
    date, hm_(request.hour), stylist, safe_(request.service), safe_(request.name), formatPhone_(request.phone), ACTIVE, '', '', new Date(),
  ]);
  recent.push(Date.now());
  props.setProperty('recent', JSON.stringify(recent));
  return done_(stylist, request);
}

// ------------------------------------------------------------------------------------- tabeli lugemine

function readState_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tz = ss.getSpreadsheetTimeZone();
  const now = nowInSalon_();
  const stylists = readStylists_(ss);
  const upcoming = readBookings_(ss, tz).filter((b) => b.date >= now.date);
  return {
    stylists,
    upcoming,
    blocked: readBlocked_(ss),
    free: freeHours_(now, stylists, readAbsences_(ss, tz), upcoming),
  };
}

// Every opening hour of the next DAYS_AHEAD days that a stylist at work has not given away yet.
function freeHours_(now, stylists, absences, bookings) {
  const free = {};
  for (let i = 0; i < DAYS_AHEAD; i++) {
    const date = addDays_(now.date, i);
    const weekday = weekday_(date);
    const open = OPENING_HOURS[weekday];
    if (!open || isAway_(absences, EVERYONE, date)) continue;
    const day = {};
    for (const stylist of stylists) {
      const shift = stylist.shifts[(weekday + 6) % 7];
      if (!shift || isAway_(absences, stylist.name, date)) continue;
      const taken = bookings.filter((b) => b.date === date && sameName_(b.stylist, stylist.name)).map((b) => b.hour);
      const hours = [];
      for (let t = open[0]; t + SLOT <= open[1] + 1e-9; t += SLOT) {
        if (t < shift[0] - 1e-9 || t + SLOT > shift[1] + 1e-9) continue;
        if (i === 0 && t < now.hour + SLOT) continue;
        // a booking written in by hand at, say, 10:30 keeps both 10:00 and 11:00
        if (taken.some((h) => h < t + SLOT && t < h + SLOT)) continue;
        hours.push(t);
      }
      if (hours.length) day[stylist.name] = hours;
    }
    if (Object.keys(day).length) free[date] = day;
  }
  return free;
}

function readStylists_(ss) {
  return readRows_(ss.getSheetByName(SHEET.stylists), STYLIST_HEAD.length, true)
    .map((row) => ({ name: clean_(row[0], 40), mobile: row[1], shifts: row.slice(2).map(parseShift_) }))
    .filter((s) => s.name);
}

// A weekday cell on "Juuksurid": "x" = the whole opening day, "8-12" = only those hours, empty = not at work.
function parseShift_(cell) {
  const text = String(cell).trim();
  if (!text) return null;
  const m = text.match(/^(\d{1,2})(?:[:.](\d{2}))?\s*[-–—]\s*(\d{1,2})(?:[:.](\d{2}))?$/);
  if (!m) return [0, 24];
  return [Number(m[1]) + Number(m[2] || 0) / 60, Number(m[3]) + Number(m[4] || 0) / 60];
}

function readBookings_(ss, tz) {
  const sheet = ss.getSheetByName(SHEET.bookings);
  const last = sheet.getLastRow();
  if (last < 2) return [];
  const range = sheet.getRange(2, 1, last - 1, COL.status + 1);
  const values = range.getValues();
  const shown = range.getDisplayValues();
  return values
    .map((row, i) => ({
      date: cellDate_(row[COL.date], tz),
      hour: parseHour_(shown[i][COL.time]),
      stylist: clean_(row[COL.stylist], 40),
      phone: normalizePhone_(row[COL.phone]),
      cancelled: sameName_(row[COL.status], CANCELLED),
    }))
    .filter((b) => b.date && b.hour !== null && !b.cancelled);
}

function readAbsences_(ss, tz) {
  return readRows_(ss.getSheetByName(SHEET.absences), ABSENCE_HEAD.length, false)
    .map((row) => {
      const from = cellDate_(row[1], tz);
      return { name: clean_(row[0], 40), from, to: cellDate_(row[2], tz) || from };
    })
    .filter((a) => a.name && a.from);
}

function readBlocked_(ss) {
  return new Set(readRows_(ss.getSheetByName(SHEET.blocked), 1, true).map((row) => normalizePhone_(row[0])).filter(Boolean));
}

function readRows_(sheet, width, display) {
  const last = sheet.getLastRow();
  if (last < 2) return [];
  const range = sheet.getRange(2, 1, last - 1, width);
  return display ? range.getDisplayValues() : range.getValues();
}

function isAway_(absences, name, date) {
  return absences.some((a) => sameName_(a.name, name) && a.from <= date && date <= a.to);
}

// ---------------------------------------------------------------------------------------- tabeli menüü

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Broneerimine')
    .addItem('Blokeeri valitud rea number', 'blokeeriNumber')
    .addSeparator()
    .addItem('Peata netibroneerimine', 'peataBroneerimine')
    .addItem('Ava netibroneerimine', 'avaBroneerimine')
    .addSeparator()
    .addItem('Seadista tabel', 'seadista')
    .addToUi();
}

function peataBroneerimine() {
  PropertiesService.getScriptProperties().setProperty('paused', 'käsitsi');
  say_('Netibroneerimine on peatatud. Veebilehe vorm ütleb, et aja saab kinni panna telefonil.');
}

function avaBroneerimine() {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('paused');
  props.deleteProperty('recent');
  say_('Netibroneerimine on jälle avatud.');
}

// Select a row on "Broneeringud" first: its number can no longer book online and its upcoming bookings are cancelled.
function blokeeriNumber() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ui = SpreadsheetApp.getUi();
  const sheet = ss.getActiveSheet();
  const row = sheet.getActiveRange().getRow();
  if (sheet.getName() !== SHEET.bookings || row < 2) {
    ui.alert(`Vali lehel „${SHEET.bookings}” see rida, mille telefoninumbrit tahad blokeerida.`);
    return;
  }
  const phone = normalizePhone_(sheet.getRange(row, COL.phone + 1).getDisplayValue());
  if (!phone) {
    ui.alert('Sellel real ei ole Eesti mobiilinumbrit.');
    return;
  }
  const tz = ss.getSpreadsheetTimeZone();
  const today = nowInSalon_().date;
  const values = sheet.getRange(2, 1, sheet.getLastRow() - 1, COL.status + 1).getValues();
  const rows = [];
  values.forEach((v, i) => {
    if (normalizePhone_(v[COL.phone]) === phone && cellDate_(v[COL.date], tz) >= today && !sameName_(v[COL.status], CANCELLED)) rows.push(i + 2);
  });
  const answer = ui.alert(
    `Blokeeri ${formatPhone_(phone)}?`,
    `See number ei saa enam netis aega broneerida. Selle numbri tulevased broneeringud (${rows.length}) märgin tühistatuks.`,
    ui.ButtonSet.YES_NO
  );
  if (answer !== ui.Button.YES) return;
  ss.getSheetByName(SHEET.blocked).appendRow([formatPhone_(phone), 'Blokeeritud broneeringute lehelt', new Date()]);
  rows.forEach((r) => sheet.getRange(r, COL.status + 1).setValue(CANCELLED));
  ss.toast(`${formatPhone_(phone)} on blokeeritud.`);
}

// Builds the tabs, headings, formats and drop-downs. Safe to run again: it never removes rows.
function seadista() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  ss.setSpreadsheetTimeZone(TIME_ZONE);
  ss.setSpreadsheetLocale('et_EE');

  // a new spreadsheet's own empty first tab becomes "Broneeringud" instead of lying around
  const first = ss.getSheets()[0];
  if (!ss.getSheetByName(SHEET.bookings) && ss.getSheets().length === 1 && first.getLastRow() === 0) first.setName(SHEET.bookings);
  const tab = (name, index) => ss.getSheetByName(name) || ss.insertSheet(name, Math.min(index, ss.getSheets().length));
  const bookings = tab(SHEET.bookings, 0);
  const overview = tab(SHEET.overview, 0);
  const stylistsNew = !ss.getSheetByName(SHEET.stylists);
  const stylists = tab(SHEET.stylists, 2);
  const absences = tab(SHEET.absences, 3);
  const blocked = tab(SHEET.blocked, 4);

  head_(stylists, STYLIST_HEAD);
  stylists.getRange('B:I').setNumberFormat('@');
  if (stylistsNew) {
    stylists.getRange(2, 1, FIRST_STYLISTS.length, STYLIST_HEAD.length)
      .setValues(FIRST_STYLISTS.map((name) => [name, '', 'x', 'x', 'x', 'x', 'x', 'x', '']));
  }
  stylists.getRange('B1').setNote('Juuksuri mobiilinumber. Järgmises etapis saadame siia SMSi iga uue broneeringu kohta.');
  stylists.getRange('C1').setNote('Iga päeva all:\nx = terve päev\n8-12 = ainult need tunnid\ntühi = ei tööta sel päeval');
  stylists.setColumnWidth(1, 140);
  stylists.setColumnWidth(2, 130);
  stylists.setColumnWidths(3, 7, 60);

  head_(bookings, BOOKING_HEAD);
  bookings.getRange('A2:A').setNumberFormat(DATE_FORMAT);
  bookings.getRange('B2:B').setNumberFormat(TIME_FORMAT);
  bookings.getRange('F2:F').setNumberFormat('@');
  bookings.getRange('J2:J').setNumberFormat(STAMP_FORMAT);
  bookings.getRange('C2:C').setDataValidation(SpreadsheetApp.newDataValidation()
    .requireValueInRange(stylists.getRange('A2:A'), true).setAllowInvalid(false).build());
  bookings.getRange('G2:G').setDataValidation(SpreadsheetApp.newDataValidation()
    .requireValueInList([ACTIVE, CANCELLED], true).setAllowInvalid(false).build());
  bookings.getRange('H2:H').setDataValidation(SpreadsheetApp.newDataValidation()
    .requireValueInList(['Tuli', 'Ei tulnud'], true).setAllowInvalid(false).build());
  bookings.setConditionalFormatRules([
    SpreadsheetApp.newConditionalFormatRule()
      .whenFormulaSatisfied(`=$G2="${CANCELLED}"`)
      .setFontColor('#8a8d96').setStrikethrough(true)
      .setRanges([bookings.getRange('A2:J')]).build(),
  ]);
  bookings.getRange('A1').setNote('Kõik broneeringud. Käsitsi broneeringu (telefon, Messenger) jaoks lisa uus rida: kuupäev, kell, juuksur ja klient. Siis kaob see aeg ka veebilehelt.');
  bookings.getRange('G1').setNote(`${CANCELLED} = aeg vabaneb jälle veebilehel.`);
  [120, 60, 100, 150, 150, 130, 100, 90, 200, 130].forEach((w, i) => bookings.setColumnWidth(i + 1, w));

  overview.getRange('A1').setValue('Juuksur').setFontWeight('bold');
  if (!overview.getRange('B1').getValue()) overview.getRange('B1').setValue(EVERYONE);
  overview.getRange('Z1').setValue(EVERYONE);
  overview.getRange('Z2').setFormula(`=FILTER(${SHEET.stylists}!A2:A, ${SHEET.stylists}!A2:A<>"")`);
  overview.hideColumns(26);
  overview.getRange('B1').setDataValidation(SpreadsheetApp.newDataValidation()
    .requireValueInRange(overview.getRange('Z1:Z'), true).setAllowInvalid(false).build()).setFontWeight('bold');
  overview.getRange('D1').setValue('Kõik tulevased broneeringud kuupäeva järgi. Ühe juuksuri omad näed, kui valid tema nime lahtrist B1.').setFontColor('#5a5d67');
  overview.getRange(3, 1, 1, 6).setValues([BOOKING_HEAD.slice(0, 6)]).setFontWeight('bold');
  overview.setFrozenRows(3);
  overview.getRange('A4').setFormula(
    `=IFERROR(SORT(FILTER(${SHEET.bookings}!A2:F, ${SHEET.bookings}!A2:A>=TODAY(), ${SHEET.bookings}!G2:G<>"${CANCELLED}", ` +
    `(B1="${EVERYONE}")+(${SHEET.bookings}!C2:C=B1)), 1, TRUE, 2, TRUE), "Tulevasi broneeringuid ei ole")`
  );
  overview.getRange('A4:A').setNumberFormat(DATE_FORMAT);
  overview.getRange('B4:B').setNumberFormat(TIME_FORMAT);
  [120, 60, 100, 150, 150, 130].forEach((w, i) => overview.setColumnWidth(i + 1, w));

  head_(absences, ABSENCE_HEAD);
  absences.getRange('B2:C').setNumberFormat('dd.mm.yyyy');
  absences.getRange('A1').setNote(`Juuksuri nimi. Kui kogu salong on kinni (näiteks riigipühal), kirjuta ${EVERYONE}.`);
  absences.getRange('C1').setNote('Tühi = ainult see üks päev.');
  [140, 110, 110, 220].forEach((w, i) => absences.setColumnWidth(i + 1, w));

  head_(blocked, BLOCKED_HEAD);
  blocked.getRange('A2:A').setNumberFormat('@');
  blocked.getRange('C2:C').setNumberFormat(STAMP_FORMAT);
  blocked.getRange('A1').setNote('Nendelt numbritelt netibroneeringuid vastu ei võeta.');
  [140, 260, 130].forEach((w, i) => blocked.setColumnWidth(i + 1, w));

  ss.setActiveSheet(overview);
  say_('Tabel on valmis. Vaata üle leht „Juuksurid” (nimed ja tööpäevad) ja avalda siis script veebirakendusena (juhend: README.md).');
}

function head_(sheet, head) {
  sheet.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight('bold');
  sheet.setFrozenRows(1);
}

// ------------------------------------------------------------------------------------------------ abi

function done_(stylist, request) {
  return { ok: true, stylist, date: request.date, time: hm_(request.hour) };
}

function fail_(error, message) {
  return { ok: false, error, message };
}

function json_(value) {
  return ContentService.createTextOutput(JSON.stringify(value)).setMimeType(ContentService.MimeType.JSON);
}

function isPaused_() {
  return Boolean(PropertiesService.getScriptProperties().getProperty('paused'));
}

function alertOwner_() {
  try {
    const to = ALERT_EMAIL || Session.getEffectiveUser().getEmail();
    MailApp.sendEmail(to, 'Leola: netibroneerimine pandi pausile',
      `Viimase ${SPAM_MINUTES} minuti jooksul tuli ${SPAM_COUNT} netibroneeringut, seega panin netibroneerimise igaks juhuks pausile. ` +
      `Veebilehe vorm ütleb praegu, et aja saab kinni panna telefonil.\n\n` +
      `Vaata broneeringud üle: ${SpreadsheetApp.getActiveSpreadsheet().getUrl()}\n\n` +
      `Kui need on päris broneeringud: tabeli menüüst Broneerimine → Ava netibroneerimine.\n` +
      `Kui need on võltsid: vali võltsi rida ja Broneerimine → Blokeeri valitud rea number. Seejärel ava netibroneerimine.`);
  } catch (error) {
    console.error(error);
  }
}

function say_(message) {
  try {
    SpreadsheetApp.getUi().alert(message);
  } catch (error) {
    console.log(message);
  }
}

// Today's date and the hour (10.5 = 10:30) on the salon's clock.
function nowInSalon_() {
  const parts = Utilities.formatDate(new Date(), TIME_ZONE, 'yyyy-MM-dd HH mm').split(' ');
  return { date: parts[0], hour: Number(parts[1]) + Number(parts[2]) / 60 };
}

function addDays_(date, days) {
  const p = date.split('-').map(Number);
  return new Date(Date.UTC(p[0], p[1] - 1, p[2] + days)).toISOString().slice(0, 10);
}

function weekday_(date) {
  const p = date.split('-').map(Number);
  return new Date(Date.UTC(p[0], p[1] - 1, p[2])).getUTCDay();
}

// A date cell as yyyy-mm-dd: a real date, or text typed as 2026-10-15, 15.10.2026 or 15.10.
function cellDate_(value, tz) {
  if (Object.prototype.toString.call(value) === '[object Date]') return isNaN(value) ? '' : Utilities.formatDate(value, tz, 'yyyy-MM-dd');
  const text = String(value).trim();
  let m = text.match(/^(\d{4})-(\d{1,2})-(\d{1,2})$/);
  if (m) return ymd_(m[1], m[2], m[3]);
  m = text.match(/^(\d{1,2})\.(\d{1,2})\.?(\d{4})?$/);
  if (m) return ymd_(m[3] || nowInSalon_().date.slice(0, 4), m[2], m[1]);
  return '';
}

function ymd_(y, m, d) {
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
}

// "10:00", "9.30" or "10" as hours (9.5); anything else is null.
function parseHour_(value) {
  const m = String(value === undefined || value === null ? '' : value).trim().match(/^(\d{1,2})(?:[:.](\d{2})(?::\d{2})?)?$/);
  if (!m) return null;
  const hour = Number(m[1]) + Number(m[2] || 0) / 60;
  return hour < 24 ? hour : null;
}

function hm_(hour) {
  return `${String(Math.floor(hour)).padStart(2, '0')}:${String(Math.round((hour % 1) * 60)).padStart(2, '0')}`;
}

// An Estonian mobile number as bare digits (51234567), with or without +372; anything else is null.
function normalizePhone_(value) {
  const digits = String(value === undefined || value === null ? '' : value).replace(/\D/g, '').replace(/^(00)?372(?=\d{7,8}$)/, '');
  return /^[58]\d{6,7}$/.test(digits) ? digits : null;
}

function formatPhone_(digits) {
  const cut = digits.length === 8 ? 4 : 3;
  return `+372 ${digits.slice(0, cut)} ${digits.slice(cut)}`;
}

function sameName_(a, b) {
  return String(a).trim().toLowerCase() === String(b).trim().toLowerCase();
}

// One line of plain text, at most max characters.
function clean_(value, max) {
  return String(value === undefined || value === null ? '' : value).replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max);
}

// Text from the web never becomes a formula in the sheet.
function safe_(text) {
  return /^[=+\-@]/.test(text) ? `'${text}` : text;
}
