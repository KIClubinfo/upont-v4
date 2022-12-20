import React from 'react';

interface Props {
    course: {
        name: string;
        acronym: string;
        departement: string;
    }
}

export const Course: React.FC<Props> = (props) => {
    return (
        <div>
            <div className="course-card">
                <div className="course-information">
                    <span className="course-name">{props.course.name} ({props.course.acronym})</span>
                    <span className="course-departement">{props.course.departement}</span>
                </div>
            </div>
        </div>
    )
}