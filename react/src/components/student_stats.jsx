import React from 'react'
import { PieChart, Pie, ResponsiveContainer } from 'recharts'
import { useAsync } from 'react-async'

async function fetchStats ({ studentId }) {
  const requestUrl = new URL(window.location.origin + Urls.student_stats())
  requestUrl.searchParams.set('student', studentId)
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

export default function StudentStats (props) {
  const { data, error } = useAsync({ promiseFn: fetchStats, studentId: props.studentId })
  if (error) {
    console.error(error)
  }

  if (data) {
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
  } else {
    // Render nothing while the data are not yed fetch
    return (<></>)
  }
}
