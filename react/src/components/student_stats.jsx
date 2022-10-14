import React from 'react'
import { PieChart, Pie, ResponsiveContainer } from 'recharts'
import { useAsync } from 'react-async'

async function fetchAlcohols () {
  const response = await fetch(Urls.student_stats())
    .then(
      result => {
        return result.json()
      },
      error => {
        console.error('Error fetching data: ' + error)
      }
    )
  return response.alcohols
}

export default function StudentStats () {
  const { data, error } = useAsync({ promiseFn: fetchAlcohols })
  if (error) {
    console.error(error)
  }

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={data}
            dataKey='num_buy'
            cx='50%'
            cy='50%'
            fill='#82ca9d'
            label={(entry) => entry.name}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
