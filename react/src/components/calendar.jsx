import React, { useMemo, useState, useEffect } from 'react';
import { useAsync } from 'react-async';
import PropTypes from 'prop-types';
import moment from 'moment';
import 'moment/locale/fr';

import { Calendar, DateLocalizer, momentLocalizer } from 'react-big-calendar';

import * as dates from './utils/dates';

// Set the calendar language to french
moment.locale('fr');
const mLocalizer = momentLocalizer(moment);

const messages = {
  allDay: 'journée',
  previous: 'précédent',
  next: 'suivant',
  today: "aujourd'hui",
  month: 'mois',
  week: 'semaine',
  day: 'jour',
  agenda: 'Agenda',
  date: 'date',
  time: 'heure',
  event: 'événement',
  showMore: (total) => `+ ${total} événement(s) supplémentaire(s)`,
};

// Data fetching from back API
const eventType = {
  EVENT: 1,
  COURSE: 2,
};

async function getEvents() {
  const response = await fetch('/api/events').then(
    (result) => result.json(),
    (error) => {
      // eslint-disable-next-line no-console
      console.error(`Error fetching the events: ${error}`);
    },
  );

  const rawEvents = response.results;

  const formattedEvents = []; // Events formatted for BigCalendar
  for (const e of rawEvents) {
    formattedEvents.push({
      id: e.id,
      type: eventType.EVENT,
      title: e.name,
      desc: e.description,
      start: new Date(e.date),
      end: new Date(e.end),
    });
  }

  return formattedEvents;
}

async function getCourses() {
  // eslint-disable-next-line no-undef
  const response = await fetch(`${Urls.timeslotList()}?is_enrolled=true`).then(
    (result) => result.json(),
    (error) => {
      // eslint-disable-next-line no-console
      console.error(`Error fetching the courses: ${error}`);
    },
  );

  const rawCourses = response.results;

  const formattedCourses = []; // Courses formatted for BigCalendar
  for (const c of rawCourses) {
    formattedCourses.push({
      id: c.id,
      type: eventType.COURSE,
      title: c.course_name,
      start: new Date(c.start),
      end: new Date(c.end),
    });
  }

  return formattedCourses;
}

function handleSelectedEvent(e) {
  if (e.type === eventType.EVENT) {
    const serveurUrl = window.location.origin;
    window.open(`${serveurUrl}/news/event/${e.id}/detail`, '_blank');
  }
}

export default function EventCalendar({ localizer }) {
  const { components, defaultDate, max, views } = useMemo(
    () => ({
      defaultDate: new Date(Date.now()),
      max: dates.add(dates.endOf(new Date(2024, 17, 1), 'day'), -1, 'hours'),
      views: {
        agenda: true,
        month: true,
        week: true,
        day: true,
      },
    }),
    [],
  );

  const [events, setEvents] = useState([]);
  const [courses, setCourses] = useState([]);
  const [shownOnCalendar, setShownOnCalendar] = useState([]);

  useEffect(() => {
    (async () => {
      const fetchedEvents = await getEvents();
      setEvents(fetchedEvents);
    })();
  }, []);

  useEffect(() => {
    (async () => {
      const fetchedCourses = await getCourses();
      setCourses(fetchedCourses);
    })();
  }, []);

  // Update showedEvents when data value change or a filter state is changed
  useEffect(() => {
    setShownOnCalendar([].concat(events, courses));
  }, [events, courses]);

  // Manage default calendar view for small monitor like smartphones
  let defaultView;
  if (window.innerWidth < 700) {
    defaultView = 'day';
  } else {
    defaultView = 'week';
  }

  return (
    <div className="calendar-box box">
      <Calendar
        components={components}
        messages={messages}
        defaultDate={defaultDate}
        events={shownOnCalendar}
        localizer={localizer}
        max={max}
        showMultiDayTimes
        step={60}
        defaultView={defaultView}
        views={views}
        onSelectEvent={(e) => handleSelectedEvent(e)}
      />
    </div>
  );
}
EventCalendar.propTypes = {
  localizer: PropTypes.instanceOf(DateLocalizer),
};

EventCalendar.defaultProps = {
  localizer: mLocalizer,
};
