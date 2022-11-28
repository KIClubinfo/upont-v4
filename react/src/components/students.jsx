import React from 'react';
import InfiniteScroll from 'react-infinite-scroller';

function Student(props) {
  return (
    <div className="col-xxl-2 col-xl-3 col-lg-4 col-sm-6">
      <div className="user-card">
        <div className="user-image">
          <img className="image-centered" src={props.picture_url} alt=""></img>
        </div>
        <div className="user-information">
          <span className="user-name">
            {props.student.user.first_name} {props.student.user.last_name}
          </span>
          <span>
            {props.student.department} - Promo '{props.student.promo.nickname}
          </span>
        </div>
        <a href={props.student.profile_url} className="stretched-link"></a>
      </div>
    </div>
  );
}

class Students extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      error: null,
      students: [],
      next_url: Urls['students'](),
      count: null,
      more_exist: true,
      loading: false,
    };
  }

  componentDidMount() {}

  fetchData = () => {
    this.setState({ more_exist: false });
    fetch(this.state.next_url)
      .then((res) => res.json())
      .then(
        (result) => {
          var has_more = false;
          if (result.next) {
            has_more = true;
          } else {
            result.next = '';
          }
          this.setState({
            next_url: '/' + result.next.replace(/^(?:\/\/|[^/]+)*\//, ''),
            students: this.state.students.concat(result.results),
            more_exist: has_more,
          });
        },
        (error) => {
          this.setState({
            error,
          });
        },
      );
  };

  render() {
    return (
      <InfiniteScroll
        loadMore={this.fetchData}
        hasMore={this.state.more_exist}
        loader={
          <div key="-1" style={{ textAlign: 'center', marginTop: '10%' }}>
            <i className="fa fa-lg fa-spinner fa-spin"></i>
          </div>
        }
      >
        <div className="row" key="-2">
          {this.state.students.map(function f(student) {
            return (
              <Student
                student={student}
                picture_url={student.picture_url}
                key={student.user.id}
              />
            );
          })}
        </div>
      </InfiniteScroll>
    );
  }
}

export default Students;
