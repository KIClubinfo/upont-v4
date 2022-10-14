import ReactDOM from 'react-dom'
import React from 'react'
import StudentStats from './components/student_stats'

fetch(Urls.current_student())
  .then(
    result => {
      return result.json()
    })
  .then(
    data => {
      ReactDOM.render((
        <StudentStats studentId={data.student.id} />
      ), window.react_mount)
    })
  .catch(
    error => {
      console.error('Error fetching current student data: ' + error)
    })
