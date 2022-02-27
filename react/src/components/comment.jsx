import React from 'react';


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
    if (state.comment.club) {
        return (
            <div className="news-card-comment-box">
                <span className="text-bold">{state.comment.club.name}</span><br></br>{state.comment.content}
            </div>
        )
    }
    else {
        return (
            <div className="news-card-comment-box">
                <span className="text-bold">{state.comment.author.user.first_name} {state.comment.author.user.last_name}</span><br></br>{state.comment.content}
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
        const url = this.state.comment.comment_delete_url;
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