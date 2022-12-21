import React, { useState } from 'react';
import { setDatasets } from 'react-chartjs-2/dist/utils';
import InfiniteScroll from 'react-infinite-scroller';
import { fetchPaginatedData } from '../utils/utils'
import { Course } from './CourseComponent';

export const Courses: React.FC = () => {
    const [courses, setCourses] = useState([]);
    // @ts-ignore Urls is declared in the django template
    const [nextUrl, setNextUrl] = useState(Urls.courseList());
    const [moreExists, setMoreExists] = useState(true);
    const [activeTab, setActiveTab] = useState(1);

    const fetchData = fetchPaginatedData(courses, setCourses, setMoreExists, nextUrl, setNextUrl);

    const handleChangeTab = (tabNumber, urlArg="") => () => {
        setCourses([]);
        // @ts-ignore Urls is declared in the django template
        setNextUrl(urlArg ? `${Urls.courseList()}?${urlArg}` : Urls.courseList());
        setMoreExists(true);
        setActiveTab(tabNumber)
    }

    return (
        <>
            <div className="row tab">
                <div className="col">
                    <button className={activeTab == 1 ? "active" : ""} onClick={handleChangeTab(1)} type="button">
                            Tous les cours
                    </button>
                </div>
                <div className="col">
                    <button className={activeTab == 2 ? "active": ""} onClick={handleChangeTab(2, "is_enrolled=true")} type="button">
                        Mes cours
                    </button>
                </div>
            </div>
            <InfiniteScroll
                loadMore={fetchData}
                hasMore={moreExists}
                loader={<div key="-1">Loading...</div>}
                >
            {courses.map((course) => (<Course course={course} key={course.id} />))}
            </InfiniteScroll>
        </>
    )
}