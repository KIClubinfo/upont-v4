import React, { useMemo, useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import 'moment/locale/fr';

import {
  Calendar,
  DateLocalizer,
  momentLocalizer,
  Views,
} from 'react-big-calendar';

import * as dates from 'date-arithmetic';

import ExportCalendar from './export_calendar';

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

async function getSchedule(schedule, urlParams) {
  const rawEvents = await fetch(
    // eslint-disable-next-line no-undef
    `${Urls.calendarData()}?${urlParams.toString()}`,
  ).then(
    (result) => result.json(),
    // eslint-disable-next-line no-console
    (error) => console.log(error),
  );

  const isNew = (e) =>
    !schedule.some((x) => x.id === e.id && x.type === e.type);

  const newEvents = [];
  for (const e of rawEvents) {
    if (isNew(e)) {
      newEvents.push({
        id: e.id,
        type: e.type,
        title: e.title,
        start: new Date(e.start),
        end: new Date(e.end),
      });
    }
  }

  return newEvents;
}

function handleSelectedEvent(e) {
  if (e.type === 'event') {
    const serveurUrl = window.location.origin;
    window.open(`${serveurUrl}/news/event/${e.id}/detail`, '_blank');
  }
}

function eventStyleGetter(event) {
  let backgroundColor = '#3DC1F3';
  if (event.type === 'course') {
    backgroundColor = '#150578';
  }

  const style = {
    backgroundColor,
    borderRadius: '2px',
    opacity: 1,
    color: 'white',
    border: '0px',
    display: 'block',
  };
  return { style };
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

  const tabs = {
    EVENTS: 1,
    SCHEDULE: 2,
  };

  const [schedule, setSchedule] = useState([]);
  const [fetchedRange, setFetchedRange] = useState({
    start: dates.add(dates.startOf(new Date(), 'day'), -10, 'day'),
    end: dates.add(dates.endOf(new Date(), 'day'), 10, 'day'),
  });
  const [activeTab, setActiveTab] = useState(tabs.EVENTS);
  const [urlParams, setUrlParams] = useState(
    new URLSearchParams({
      start: fetchedRange.start.toISOString(),
      end: fetchedRange.end.toISOString(),
      courses: 'false',
    }),
  );

  useEffect(() => {
    (async () => {
      const fetchedSchedule = await getSchedule(schedule, urlParams);
      setSchedule((prev) => fetchedSchedule.concat(prev));
    })();
  }, [urlParams]);

  const handleChangeTab = (tab) => () => {
    if (tab !== activeTab) {
      setSchedule([]);
      if (tab === tabs.EVENTS) {
        setUrlParams((prev) => {
          prev.set('start', fetchedRange.start.toISOString());
          prev.set('end', fetchedRange.end.toISOString());
          prev.set('courses', 'false');
          prev.delete('is_enrolled');
          return new URLSearchParams(prev);
        });
      } else if (tab === tabs.SCHEDULE) {
        setUrlParams((prev) => {
          prev.set('start', fetchedRange.start.toISOString());
          prev.set('end', fetchedRange.end.toISOString());
          prev.set('courses', 'true');
          prev.set('is_enrolled', 'true');
          return new URLSearchParams(prev);
        });
      }
      setActiveTab(tab);
    }
  };

  const onRangeChange = useCallback(
    (range) => {
      let start;
      let end;
      if (range.start && range.end) {
        start = range.start;
        end = range.end;
      } else {
        [start] = range;
        end = dates.add(range.slice(-1), 1, 'day');
      }

      if (start && end) {
        const startOutOfRange = dates.lt(start, fetchedRange.start);
        const endOutOfRange = dates.gt(end, fetchedRange.end);

        if (startOutOfRange && endOutOfRange) {
          setUrlParams((prev) => {
            prev.set('start', start.toISOString());
            prev.set('end', end.toISOString());
            return new URLSearchParams(prev);
          });
          setFetchedRange({ start, end });
        } else if (startOutOfRange) {
          setUrlParams((prev) => {
            prev.set('start', start.toISOString());
            prev.set('end', fetchedRange.start.toISOString());
            return new URLSearchParams(prev);
          });
          setFetchedRange((prev) => ({ start, end: prev.end }));
        } else if (endOutOfRange) {
          setUrlParams((prev) => {
            prev.set('start', fetchedRange.end.toISOString());
            prev.set('end', end.toISOString());
            return new URLSearchParams(prev);
          });
          setFetchedRange((prev) => ({ start: prev.start, end }));
        }
      }
    },
    [urlParams, setUrlParams, fetchedRange, setFetchedRange],
  );

  // Manage default calendar view for small monitor like smartphones
  let defaultView;
  if (window.innerWidth < 700) {
    defaultView = Views.DAY;
  } else {
    defaultView = Views.WEEK;
  }

  return (
    <>
      <div className="row tab">
        <div className="col">
          <button
            className={activeTab === tabs.EVENTS ? 'active' : ''}
            onClick={handleChangeTab(tabs.EVENTS)}
            type="button"
          >
            Tous les events
          </button>
        </div>
        <div className="col">
          <button
            className={activeTab === tabs.SCHEDULE ? 'active' : ''}
            onClick={handleChangeTab(tabs.SCHEDULE)}
            type="button"
          >
            Mon emploi du temps
          </button>
        </div>
      </div>
      <div className="calendar-box box">
        {activeTab === tabs.SCHEDULE ? <ExportCalendar /> : null}
        <Calendar
          components={components}
          messages={messages}
          defaultDate={defaultDate}
          events={schedule}
          localizer={localizer}
          max={max}
          showMultiDayTimes
          step={60}
          defaultView={defaultView}
          views={views}
          onSelectEvent={(e) => handleSelectedEvent(e)}
          onRangeChange={onRangeChange}
          eventPropGetter={eventStyleGetter}
        />
      </div>
    </>
  );
}
EventCalendar.propTypes = {
  localizer: PropTypes.instanceOf(DateLocalizer),
};

EventCalendar.defaultProps = {
  localizer: mLocalizer,
};
