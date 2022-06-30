import React, { Fragment, useMemo } from 'react'
import { useAsync } from 'react-async'
import PropTypes from 'prop-types'
import moment from 'moment'

import {
  Calendar,
  Views,
  DateLocalizer,
  momentLocalizer
} from 'react-big-calendar'

import DemoLink from './calendar_example/DemoLink.component.js'
import * as dates from './calendar_example/dates'

const mLocalizer = momentLocalizer(moment)

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

/**
 * We are defaulting the localizer here because we are using this same
 * example on the main 'About' page in Storybook
 */

export default function Basic ({
  localizer = mLocalizer,
  showDemoLink = true,
  ...props
}) {
  const { components, defaultDate, max, views } = useMemo(
    () => ({
      components: {
        timeSlotWrapper: ColoredDateCellWrapper
      },
      defaultDate: new Date(2022, 3, 1),
      max: dates.add(dates.endOf(new Date(2015, 17, 1), 'day'), -1, 'hours'),
      views: Object.keys(Views).map((k) => Views[k])
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
