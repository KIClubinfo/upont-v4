import React, { useState, useEffect } from 'react'
import { PieChart, Pie, ResponsiveContainer } from 'recharts'
import DatePicker from 'react-datepicker'

async function fetchStats (studentId, startDate, endDate) {
  const requestUrl = new URL(window.location.origin + Urls.student_stats())
  requestUrl.searchParams.set('student', studentId)
  if (startDate) {
    requestUrl.searchParams.set('start', startDate.toISOString())
  }
  if (endDate) {
    requestUrl.searchParams.set('end', endDate.toISOString())
  }

  const response = await fetch(requestUrl)
    .then(
      result => {
        return result.json()
      },
      error => {
        console.error('Error fetching data: ' + error)
      }
    )
  return response
}

function AlcoholsPieChart (props) {
  return (
    <ResponsiveContainer>
      <PieChart>
        <Pie
          data={props.data}
          dataKey='num_buy'
          cx='50%'
          cy='50%'
          fill='#82ca9d'
          label={(entry) => entry.name}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

function StatsViewer (props) {
  const { data } = props

  return (
    <>
      <p>Volume total ingéré : {(data.total_volume / 1000).toLocaleString(
        'fr-FR',
        {
          style: 'unit',
          unit: 'liter',
          maximumFractionDigits: 3,
          minimumFractionDigits: 3
        }
      )}
      </p>
      <div style={{ width: '100%', height: 300 }}>
        <AlcoholsPieChart data={data.alcohols} />
      </div>
    </>
  )
}

export default function StudentStats (props) {
  const [dateRange, setDateRange] = useState([null, null])
  const [startDate, endDate] = dateRange

  const [data, setData] = useState()

  useEffect(() => {
    const fetchData = async () => {
      const newData = await fetchStats(props.studentId, startDate, endDate)

      setData(newData)
    }

    void fetchData()
  }, [endDate])

  if (data) {
    return (
      <>
        <DatePicker
          selectsRange
          startDate={startDate}
          endDate={endDate}
          onChange={(update) => {
            setDateRange(update)
          }}
          withPortal
        />
        <StatsViewer data={data} />
      </>
    )
  } else {
    // Render nothing while the data are not yet fetch
    return (<></>)
  }
}
