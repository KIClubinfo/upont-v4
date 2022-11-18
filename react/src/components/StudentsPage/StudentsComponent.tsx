import 'react';
import { useState } from 'react';
import InfiniteScroll from 'react-infinite-scroller';
import { Student } from "./StudentComponent";


export const Students: React.FC = () => {
    const [students, setStudents] = useState([])
    //@ts-ignore Urls is declared in the django template
    const [nextUrl, setNextUrl] = useState(Urls["student-list"]())
    const [moreExists, setMoreExists] = useState(true)

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
                    setStudents(students.concat(result.results));
                    setNextUrl("/" + result.next.replace(/^(?:\/\/|[^/]+)*\//, ''));
                    setMoreExists(hasMore);
                }
            )
    }

    return (
        <InfiniteScroll
            loadMore={fetchData}
            hasMore={moreExists}
            loader={<div key="-1" style={{ "textAlign": "center", "marginTop": "10%" }}><i className="fa fa-lg fa-spinner fa-spin"></i></div>}
            >
            <div className="row" key="-2">
                {
                    students.map((student) => (<Student student={student} picture_url={student.picture_url} key={student.user.id} />))
                }
            </div>
        </InfiniteScroll>
    )
}
