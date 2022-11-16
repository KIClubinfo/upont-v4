import React, { Fragment } from 'react'

const linkBase =
  'https://github.com/jquense/react-big-calendar/blob/master/stories/demos/exampleCode/'

export default function DemoLink ({ fileName, children }) {
  return (
    <>
      <div style={{ marginBottom: 10 }}>
        <a target='_blank' href={`${linkBase}${fileName}.js`} rel='noreferrer'>
          &lt;\&gt; View Example Source Code
        </a>
      </div>
      {children ? <div style={{ marginBottom: 10 }}>{children}</div> : null}
    </>
  )
}
