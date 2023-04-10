/* eslint no-fallthrough: off */
import * as dates from 'date-arithmetic';

export {
  milliseconds,
  seconds,
  minutes,
  hours,
  month,
  startOf,
  endOf,
  add,
  eq,
  neq,
  gte,
  gt,
  lte,
  lt,
  inRange,
  min,
  max,
} from 'date-arithmetic';

const MILLI = {
  seconds: 1000,
  minutes: 1000 * 60,
  hours: 1000 * 60 * 60,
  day: 1000 * 60 * 60 * 24,
};

const MONTHS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];

export function monthsInYear(year) {
  const date = new Date(year, 0, 1);

  return MONTHS.map((i) => dates.month(date, i));
}

export function firstVisibleDay(date, localizer) {
  const firstOfMonth = dates.startOf(date, 'month');

  return dates.startOf(firstOfMonth, 'week', localizer.startOfWeek());
}

export function lastVisibleDay(date, localizer) {
  const endOfMonth = dates.endOf(date, 'month');

  return dates.endOf(endOfMonth, 'week', localizer.startOfWeek());
}

export function visibleDays(date, localizer) {
  let current = firstVisibleDay(date, localizer);
  const last = lastVisibleDay(date, localizer);
  const days = [];

  while (dates.lte(current, last, 'day')) {
    days.push(current);
    current = dates.add(current, 1, 'day');
  }

  return days;
}

export function ceil(date, unit) {
  const floor = dates.startOf(date, unit);

  return dates.eq(floor, date) ? floor : dates.add(floor, 1, unit);
}

export function range(start, end, unit = 'day') {
  let current = start;
  const days = [];

  while (dates.lte(current, end, unit)) {
    days.push(current);
    current = dates.add(current, 1, unit);
  }

  return days;
}

export function merge(date0, time0) {
  if (time0 == null && date0 == null) return null;

  let time;
  if (time0 == null) {
    time = new Date();
  } else {
    time = time0;
  }

  let date;
  if (date0 == null) {
    date = new Date();
  } else {
    date = date0;
  }

  date = dates.startOf(date, 'day');
  date = dates.hours(date, dates.hours(time));
  date = dates.minutes(date, dates.minutes(time));
  date = dates.seconds(date, dates.seconds(time));
  return dates.milliseconds(date, dates.milliseconds(time));
}

export function eqTime(dateA, dateB) {
  return (
    dates.hours(dateA) === dates.hours(dateB) &&
    dates.minutes(dateA) === dates.minutes(dateB) &&
    dates.seconds(dateA) === dates.seconds(dateB)
  );
}

export function isJustDate(date) {
  return (
    dates.hours(date) === 0 &&
    dates.minutes(date) === 0 &&
    dates.seconds(date) === 0 &&
    dates.milliseconds(date) === 0
  );
}

export function duration(start, end, unit0, firstOfWeek) {
  let unit;
  if (unit0 === 'day') {
    unit = 'date';
  } else {
    unit = unit0;
  }

  return Math.abs(
    dates[unit](start, undefined, firstOfWeek) -
      dates[unit](end, undefined, firstOfWeek),
  );
}

export function diff(dateA, dateB, unit) {
  if (!unit || unit === 'milliseconds') return Math.abs(+dateA - +dateB);

  // the .round() handles an edge case
  // with DST where the total won't be exact
  // since one day in the range may be shorter/longer by an hour
  return Math.round(
    Math.abs(
      +dates.startOf(dateA, unit) / MILLI[unit] -
        +dates.startOf(dateB, unit) / MILLI[unit],
    ),
  );
}

export function total(date, unit) {
  const ms = date.getTime();
  let div = 1;

  switch (unit) {
    case 'week':
      div *= 7;
      break;
    case 'day':
      div *= 24;
      break;
    case 'hours':
      div *= 60;
      break;
    case 'minutes':
      div *= 60;
      break;
    case 'seconds':
      div *= 1000;
      break;
    default:
      throw new Error(`Unit ${unit} unknown`);
  }

  return ms / div;
}

export function week(date) {
  const d = new Date(date);
  d.setHours(0, 0, 0);
  d.setDate(d.getDate() + 4 - (d.getDay() || 7));
  return Math.ceil(((d - new Date(d.getFullYear(), 0, 1)) / 8.64e7 + 1) / 7);
}

export function today() {
  return dates.startOf(new Date(), 'day');
}

export function yesterday() {
  return dates.add(dates.startOf(new Date(), 'day'), -1, 'day');
}

export function tomorrow() {
  return dates.add(dates.startOf(new Date(), 'day'), 1, 'day');
}
