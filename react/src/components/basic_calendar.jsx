import React, { Fragment, useMemo, useState, useEffect } from 'react'
import { useAsync } from 'react-async'
import PropTypes from 'prop-types'
import moment from 'moment'
import 'moment/locale/fr'

import {
  Calendar,
  DateLocalizer,
  momentLocalizer
} from 'react-big-calendar'

import * as dates from './calendar_example/dates'

// Set the calendar language to french
moment.locale('fr')
const mLocalizer = momentLocalizer(moment)

const messages = {
  allDay: 'journée',
  previous: 'précédent',
  next: 'suivant',
  today: 'aujourd\'hui',
  month: 'mois',
  week: 'semaine',
  day: 'jour',
  agenda: 'Agenda',
  date: 'date',
  time: 'heure',
  event: 'événement',
  showMore: total => `+ ${total} événement(s) supplémentaire(s)`
}

// Events fetching from back API
async function getEvents () {
  const response = await fetch('/api/events')
    .then(
      result => {
        return result.json()
      },
      error => {
        console.error('Error getting the events: ' + error)
      }
    )

  const rawEvents = response.results

  const addOneHour = d => {
    d.setHours(d.getHours() + 1)
    return d
  }

  const formattedEvents = [] // Events formatted for BigCalendar
  for (const e of rawEvents) {
    formattedEvents.push(
      {
        id: e.id,
        title: e.name,
        desc: e.description,
        participating: e.participating,
        start: new Date(e.date),
        end: new Date(e.end),
      }
    )
  }

  return formattedEvents
}

function handleSelectedEvent (e) {
  const serveurUrl = window.location.origin
  window.open(serveurUrl + '/news/event/' + e.id + '/detail', '_blank')
}

export default function Basic ({
  localizer = mLocalizer,
  showDemoLink = false,
  ...props
}) {
  const { components, defaultDate, max, views } = useMemo(
    () => ({
      defaultDate: new Date(Date.now()),
      max: dates.add(dates.endOf(new Date(2024, 17, 1), 'day'), -1, 'hours'),
      views: {
        agenda: true,
        month: true,
        week: true,
        day: true,
      }
    }),
    []
  )

  const { data, error } = useAsync({ promiseFn: getEvents })
  if (error) {
    console.log(error.message)
  }

  const [showedEvents, setShowedEvents] = useState([])

  // State for filters
  const [onlyParticipating, setOnlyParticipating] = useState(false)

  function handleParticipating () {
    setOnlyParticipating(!onlyParticipating) // Swap the state
  }

  // Update showedEvents when data value change or a filter state is changed
  useEffect(() => {
    if (onlyParticipating) {
      setShowedEvents(data.filter(e => e.participating))
      document.getElementById('participating_button').className = 'button red-button'
    } else {
      setShowedEvents(data)
      document.getElementById('participating_button').className = 'button green-button'
    }
  }, [data, onlyParticipating])

  // Manage default calendar view for small monitor like smartphone
  var defaultView
  if (window.innerWidth < 700) {
    defaultView = 'day'
  }
  else {
    defaultView = 'week'
  }

  return (
    <>
      <div className='calendar-box box' {...props}>
        <div align='center'>
          <button className='button green-button' id='participating_button' onClick={handleParticipating}>Évènements auxquels je ne participe pas</button>
        </div>
        <Calendar
          components={components}
          messages={messages}
          defaultDate={defaultDate}
          events={showedEvents}
          localizer={localizer}
          max={max}
          showMultiDayTimes
          step={60}
          defaultView={defaultView}
          views={views}
          onSelectEvent={(e) => handleSelectedEvent(e)}
        />
      </div>
    </>
  )
}
Basic.propTypes = {
  localizer: PropTypes.instanceOf(DateLocalizer),
  showDemoLink: PropTypes.bool
}
