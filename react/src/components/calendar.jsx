import React, { useMemo, useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import 'moment/locale/fr';

import { Calendar, DateLocalizer, momentLocalizer } from 'react-big-calendar';

import * as dates from 'date-arithmetic';

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

async function getEvents(events, start, end) {
  const params = new URLSearchParams();
  params.set('start', start.toISOString());
  params.set('end', end.toISOString());
  params.set('no_page', 1);
  const rawEvents = await fetch(
    // eslint-disable-next-line no-undef
    `${Urls.eventList()}?${params.toString()}`,
  ).then(
    (result) => result.json(),
    (error) => {
      // eslint-disable-next-line no-console
      console.error(`Error fetching the events: ${error}`);
    },
  );

  const formattedEvents = []; // Events formatted for BigCalendar
  for (const e of rawEvents) {
    if (!events.some((x) => x.id === e.id)) {
      formattedEvents.push({
        id: e.id,
        type: eventType.EVENT,
        title: e.name,
        start: new Date(e.date),
        end: new Date(e.end),
      });
    }
  }

  return formattedEvents;
}

async function getCourses(courses, start, end) {
  const params = new URLSearchParams();
  params.set('start', start.toISOString());
  params.set('end', end.toISOString());
  params.set('no_page', 1);
  params.set('is_enrolled', 'true');
  const rawCourses = await fetch(
    // eslint-disable-next-line no-undef
    `${Urls.timeslotList()}?${params.toString()}`,
  ).then(
    (result) => result.json(),
    (error) => {
      // eslint-disable-next-line no-console
      console.error(`Error fetching the courses: ${error}`);
    },
  );

  const formattedCourses = []; // Courses formatted for BigCalendar
  for (const c of rawCourses) {
    if (!courses.some((x) => x.id === c.id)) {
      formattedCourses.push({
        id: c.id,
        type: eventType.COURSE,
        title: c.course_name,
        start: new Date(c.start),
        end: new Date(c.end),
      });
    }
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

  // Manage default calendar view for small monitor like smartphones
  let defaultView;
  if (window.innerWidth < 700) {
    defaultView = 'day';
  } else {
    defaultView = 'week';
  }

  const [view, setView] = useState(defaultView);
  const [events, setEvents] = useState([]);
  const [courses, setCourses] = useState([]);
  const [fetchedRange, setFetchedRange] = useState({
    start: dates.add(dates.startOf(new Date(), 'day'), -10, 'day'),
    end: dates.add(dates.endOf(new Date(), 'day'), 10, 'day'),
  });
  const [shownOnCalendar, setShownOnCalendar] = useState([]);

  useEffect(() => {
    if (events.length === 0) {
      (async () => {
        const fetchedEvents = await getEvents(
          events,
          fetchedRange.start,
          fetchedRange.end,
        );
        setEvents(fetchedEvents);
      })();

      (async () => {
        const fetchedCourses = await getCourses(
          courses,
          fetchedRange.start,
          fetchedRange.end,
        );
        setCourses(fetchedCourses);
      })();
    }
  }, []);

  // Update showedEvents when data value change or a filter state is changed
  useEffect(() => {
    setShownOnCalendar([].concat(events, courses));
  }, [events, courses]);

  const onRangeChange = useCallback(
    (range) => {
      let start;
      let end;
      console.log(view);
      if (view === 'week') {
        [start] = range;
        end = dates.add(range[6], 1, 'day');
      } else if (view === 'day') {
        [start] = range;
        end = dates.add(range[0], 1, 'day');
      } else if (view === 'month' || view === 'agenda') {
        start = range.start;
        end = range.end;
      }

      if (start && end) {
        if (dates.lt(start, fetchedRange.start)) {
          (async () => {
            const fetchedCourses = await getCourses(
              courses,
              start,
              fetchedRange.start,
            );
            setCourses((prev) => fetchedCourses.concat(prev));
          })();
          (async () => {
            const fetchedEvents = await getEvents(
              events,
              start,
              fetchedRange.start,
            );
            setEvents((prev) => fetchedEvents.concat(prev));
          })();
          setFetchedRange((prev) => ({ start, end: prev.end }));
        }

        if (dates.gt(end, fetchedRange.end)) {
          (async () => {
            const fetchedCourses = await getCourses(
              courses,
              fetchedRange.end,
              end,
            );
            setCourses((prev) => fetchedCourses.concat(prev));
          })();
          (async () => {
            const fetchedEvents = await getEvents(
              events,
              fetchedRange.end,
              end,
            );
            setEvents((prev) => fetchedEvents.concat(prev));
          })();
          setFetchedRange((prev) => ({ start: prev.start, end }));
        }
      }
    },
    [
      view,
      courses,
      setCourses,
      events,
      setEvents,
      fetchedRange,
      setFetchedRange,
    ],
  );

  const onView = useCallback((newView) => setView(newView), [setView]);

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
        onView={onView}
        view={view}
        views={views}
        onSelectEvent={(e) => handleSelectedEvent(e)}
        onRangeChange={onRangeChange}
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
