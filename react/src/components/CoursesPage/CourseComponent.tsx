import React from 'react';

interface Props {
  course: {
    id: number;
    name: string;
    acronym: string;
    department: string;
  };
}

export const Course: React.FC<Props> = (props) => (
  <a
    // @ts-ignore Urls is declared in the django template
    href={Urls['courses:course_detail'](props.course.id)}
    className="course-link"
  >
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
