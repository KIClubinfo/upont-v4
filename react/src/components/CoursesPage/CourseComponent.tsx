import { url } from 'inspector';
import React from 'react';

interface Props {
  course: {
    name: string;
    acronym: string;
    department: string;
  };
}

export const Course: React.FC<Props> = (props) => (
  <a href={Urls['courses:course_detail'](props.course.id)}>
    <div className="course-card">
      <div className="course-information">
        <span className="course-name">
          {props.course.name} ({props.course.acronym})
        </span>
        <span className="course-departement">{props.course.department}</span>
      </div>
    </div>
  </a>
);
