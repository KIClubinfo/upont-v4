import React from 'react';

interface Props {
    course: {
        name: string;
        acronynm: string;
        departement: string;
    }
}

export const Course: React.FC<Props> = (props) => {
    return (
        <div>
            <div className="course-card">
                <span className="course-name">{props.course.name} ({props.course.acronynm})</span>
                <span className="course-departement">{props.course.departement}</span>
            </div>
        </div>
    )
}