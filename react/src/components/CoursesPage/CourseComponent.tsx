import React from 'react';

interface Props {
  course: {
    name: string;
    acronym: string;
    department: string;
  };
}

export const Course: React.FC<Props> = (props) => (
  <div>
    <div className="course-card">
      <div className="course-information">
        <span className="course-name">
          {props.course.name} ({props.course.acronym})
        </span>
        <span className="course-departement">{props.course.department}</span>
      </div>
    </div>
  </div>
);
