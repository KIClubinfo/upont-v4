import React from 'react';

// auxilary functions
function addZero(i) {
    if (i < 10) {i = "0" + i}
    return i;
  }

/////////////////////////////

function comment_logo(state) {
    if (state.comment.club) {
        return (
            <div className="news-card-comment-user-pic">
                <img className="image-centered" src={state.comment.club.logo_url}></img>
            </div>
        )
    }
    else {
        return (
            <div className="news-card-comment-user-pic">
                <img className="image-centered" src={state.comment.author.picture_url}></img>
            </div>
        )
    }
}

function comment_content(state) {
    const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
    var comment_date = new Date(state.comment.date);
    let comment_hour = addZero(comment_date.getHours());
    let comment_minute = addZero(comment_date.getMinutes());
    if (state.comment.club) {
        return (
            <div className="news-card-comment-box">
                <a className="text-bold" href={state.comment.author_url}>
                    {state.comment.club.name}
                </a>
                <br/>
                <span className="news-card-header-date">
                    {comment_date.toLocaleDateString("fr-FR", options)} - {comment_hour}:{comment_minute}
                </span>
                <br/><br/>
                {state.comment.content}
            </div>
        )
    }
    else {
        return (
            <div className="news-card-comment-box">
                <a className="text-bold" href={state.comment.author_url}>
                    {state.comment.author.user.first_name} {state.comment.author.user.last_name}
                </a>
                <br/>
                <span className="news-card-header-date">
                    {comment_date.toLocaleDateString("fr-FR", options)} - {comment_hour}:{comment_minute}
                </span>
                <br/><br/>
                {state.comment.content}
            </div>
        )
    }
}


class Comment extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            comment: props.comment
        };
        this.delete = this.delete.bind(this);
        this.comment_delete_button = this.comment_delete_button.bind(this);
    }

    delete(event) {
        event.preventDefault();
        const url = Urls["news:comment_delete"](this.state.comment.id);
        const csrfmiddlewaretoken = getCookie('csrftoken');
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfmiddlewaretoken},
            body: JSON.stringify({'comment_id': this.state.comment.id})
        };
        fetch(url, requestOptions)
            .then(this.setState({
            }))
            .then(response => console.log('Deleted successfully'))
            .catch(error => console.log('Submit error', error))
        setTimeout(() => this.props.refreshPost(), 200);
    }

    comment_delete_button() {
        if (this.state.comment.is_my_comment) {
            return <a onClick={this.delete} ><i className="fas fa-times-circle"></i></a>
        }
    }

    render() {
        return (
            <div className="news-card-comments">
                <div className="news-card-comment">
                    {comment_logo(this.state)}
                    {comment_content(this.state)}
                    {this.comment_delete_button()}
                </div>
            </div>
        )
    }
}

export {Comment};