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

function comment_delete_button(state) {
    if (state.comment.is_my_comment) {
        return <a href={state.comment.comment_delete_url}><i className="fas fa-times-circle"></i></a>
    }
}

class Comment extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            comment: props.comment
        };
    }

    render() {
        return (
            <div className="news-card-comments">
                <div className="news-card-comment">
                    {comment_logo(this.state)}
                    {comment_content(this.state)}
                    {comment_delete_button(this.state)}
                </div>
            </div>
        )
    }
}

export {Comment};