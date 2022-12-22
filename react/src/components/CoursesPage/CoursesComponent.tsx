import React, { useState, useEffect } from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import AsyncSelect from 'react-select/async';
import { fetchPaginatedData } from '../utils/utils'
import { Course } from './CourseComponent';

const selectStyle = {
    option: (base) => ({
        ...base,
        // backgroundColor: '#1A1B20',
        // borderColor: '#1A1B20'
        color: 'black'
    })
}

export const Courses: React.FC = () => {
    const tabs = {
        ALL_COURSE: 1,
        ONLY_ENROLLED: 2,
    };

    const [courses, setCourses] = useState([]);
    // @ts-ignore Urls is declared in the django template
    const [nextUrl, setNextUrl] = useState(Urls.courseList());
    const [urlParams, setUrlParams] = useState(new URLSearchParams);
    const [moreExists, setMoreExists] = useState(true);
    const [activeTab, setActiveTab] = useState(tabs.ALL_COURSE);

    const fetchData = fetchPaginatedData(courses, setCourses, setMoreExists, nextUrl, setNextUrl);

    const getDepartments = () => new Promise((resolve, reject) => {
        // @ts-ignore Urls is declared in the django template
        fetch(Urls.courseDepartmentList())
        .then((res) => res.json())
        .then((departments) => {
            resolve(departments.map((dept) => ({
                value: dept,
                label: dept,
            })))
        })
        .catch(reject);
    });

    useEffect(() => {
        setMoreExists(false);
        setCourses([]);
        // @ts-ignore Urls is declared in the django template
        setNextUrl(`${Urls.courseList()}?${urlParams.toString()}`)
        setMoreExists(true);
    }, [urlParams]);

    const handleChangeTab = (tab) => () => {
        if (tab != activeTab) {
            if (tab == tabs.ONLY_ENROLLED) {
                setUrlParams((prev) => {
                    prev.set('is_enrolled', 'true');
                    return new URLSearchParams(prev);
                })
            } else {
                setUrlParams((prev) => {
                    prev.delete('is_enrolled');
                    return new URLSearchParams(prev);
                })
            }
            setActiveTab(tab);
        }
    }

    const handleDepartmentFilter = (selectedDepartment) => {
        if (selectedDepartment.length > 0) {
            setUrlParams((prev) => {
                prev.set('department', selectedDepartment.map(({ value }) => (value)).join(","));
                return new URLSearchParams(prev);
            });
        } else {
            setUrlParams((prev) => {
                prev.delete('department');
                return new URLSearchParams(prev);
            });
        }
    }

    return (
        <>
            <AsyncSelect
                isMulti
                isClearable
                isSearchable={false}
                cacheOptions
                defaultOptions
                loadOptions={getDepartments}
                onChange={handleDepartmentFilter}
                placeholder="Filtrer par départements"
                styles={selectStyle}
            />
            <div className="row tab">
                <div className="col">
                    <button className={activeTab == tabs.ALL_COURSE ? "active" : ""} onClick={handleChangeTab(tabs.ALL_COURSE)} type="button">
                            Tous les cours
                    </button>
                </div>
                <div className="col">
                    <button className={activeTab == tabs.ONLY_ENROLLED ? "active": ""} onClick={handleChangeTab(tabs.ONLY_ENROLLED)} type="button">
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