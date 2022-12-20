import React, { useState } from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import { Course } from './CourseComponent';

export const Courses: React.FC = () => {
    const [courses, setCourses] = useState([]);
    // @ts-ignore Urls is declared in the django template
    const [nextUrl, setNextUrl] = useState(Urls.courseList());
    const [moreExists, setMoreExists] = useState(true);

    const fetchData = () => {
        setMoreExists(false);
        fetch(nextUrl)
            .then(res => res.json())
            .then(
                (result) => {
                    let hasMore = false;
                    if (result.next) {
                        hasMore = true;
                    }
                    else {
                        result.next = "";
                    }
                    setCourses(courses.concat(result.results));
                    setNextUrl("/" + result.next.replace(/^(?:\/\/|[^/]+)*\//, ''));
                    setMoreExists(hasMore);
                }
            )
    }

    return (
        // <>
        // <p>Test</p>
        // <Course course={{name:"Nom", acronym:"ACR", department:"GMM"}} />
        // </>
        <InfiniteScroll
            loadMore={fetchData}
            hasMore={moreExists}
            loader={<div key="-1">Loading...</div>}
            >
        {courses.map((course) => (<Course course={course} key={course.id} />))}
        </InfiniteScroll>
    )
}