import React from 'react';
import {getCookie} from '/src/csrf'


function timeout(delay) {
    return new Promise(res => setTimeout(res, delay));
}


class CommentForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            content: '',
            post: props.post,
            club: '',
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState({ [event.target.name]: event.target.value });
    }

    handleSubmit(event) {
        event.preventDefault();
        const url = ''
        const csrfmiddlewaretoken = getCookie('csrftoken');
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfmiddlewaretoken},
            body: JSON.stringify({'content': this.state.content, 'club': this.state.club, 'post': this.state.post.id})
        };
        fetch(url, requestOptions)
            .then(this.setState({
                content: '',
                club: ''
            }))
            .then(response => console.log('Submitted successfully'))
            .catch(error => console.log('Form submit error', error))
        setTimeout(() => this.props.refreshPost(), 200);
    }

    componentDidMount() {
        fetch("/api/forms/publish/")
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({can_publish_as: result.can_publish_as})
                },
                (error) => {
                    this.setState({
                        error
                    });
                }
            )
    }

    render() {
        let options = []
        if (this.state.can_publish_as){
            for (const [key, value] of Object.entries(this.state.can_publish_as)) {
                options.push(<option key={key} value={key}>{value}</option>);
            }
        }
        let field1, field2;
        field1 =
        <div className="news-card-edit-comment">
            <div className="news-card-comment-user-pic"><img src={this.props.currentStudent.picture_url}></img></div>
            <textarea className="news-card-edit-comment-input" type="text" name="content" id="" value={this.state.content} onChange={this.handleChange}></textarea>
        </div>
        field2 =
        <div className="news-card-edit-comment">
            <select className="profil-select" name="club" id="id_club" required value={this.state.club} onChange={this.handleChange}>
                {options}
            </select>
            <button className="button green-button news-card-button" type="submit"><i className="far fa-comment"></i></button>
        </div>

        return (
            <form method="post" onSubmit={this.handleSubmit.bind(this)}>
                {field1}
                Publier en tant que :
                {field2}
                <input type="hidden" name="post" value={this.state.post.id}></input>
            </form>
        );
    }
}

export {CommentForm};