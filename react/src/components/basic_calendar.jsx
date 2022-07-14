import React, { Fragment, useMemo } from 'react'
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
  event: 'événement', // Or anything you want
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
        start: new Date(e.date),
        end: addOneHour(new Date(e.date))
      }
    )
  }

  return formattedEvents
}

const ColoredDateCellWrapper = ({ children }) =>
  React.cloneElement(React.Children.only(children), {
    style: {
      backgroundColor: 'lightblue'
    }
  })

export default function Basic ({
  localizer = mLocalizer,
  showDemoLink = false,
  ...props
}) {
  const { components, defaultDate, max, views } = useMemo(
    () => ({
      components: {
        timeSlotWrapper: ColoredDateCellWrapper
      },
      defaultDate: new Date(Date.now()),
      max: dates.add(dates.endOf(new Date(2024, 17, 1), 'day'), -1, 'hours'),
      views: {
        month: true,
        week: true
      }
    }),
    []
  )

  const { data, error } = useAsync({ promiseFn: getEvents })
  if (error) {
    console.log(error.message)
  }

  return (
    <>
      <div className='height600' {...props}>
        <Calendar
          components={components}
          messages={messages}
          defaultDate={defaultDate}
          events={data}
          localizer={localizer}
          max={max}
          showMultiDayTimes
          step={60}
          views={views}
        />
      </div>
    </>
  )
}
Basic.propTypes = {
  localizer: PropTypes.instanceOf(DateLocalizer),
  showDemoLink: PropTypes.bool
}
