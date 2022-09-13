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
        setTimeout(() => this.props.refreshPost(), 300);
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
                if (value == "Élève") {
                    // This is the option to publish as student
                    options.push(<option selected="selected" key={key} value="">{value}</option>);
                } else {
                    options.push(<option key={key} value={key}>{value}</option>);
                }
            }
        }

        const field1 =
        <div className="news-card-edit-comment">
            <textarea className="news-card-edit-comment-input" type="text" name="content" id="" value={this.state.content} onChange={this.handleChange}></textarea>
            <button className="button green-button" type="submit"><i className="fas fa-paper-plane"></i></button>
        </div>


        if (options.length > 1) {
            // The user is member of at least one club, he/she can choose to comment as a club
            const field2 =
            <div className="news-card-edit-comment">
                <select className="profil-select" name="club" id="id_club" required value={this.state.club} onChange={this.handleChange}>
                    {options}
                </select>
            </div>

            return (
            <form className="news-card-edit-comment-container" method="post" onSubmit={this.handleSubmit.bind(this)}>
                Publier en tant que :
                {field2}
                {field1}
                <input type="hidden" name="post" value={this.state.post.id}></input>
            </form>
            );
        } else {
            return (
            <form method="post" onSubmit={this.handleSubmit.bind(this)}>
                {field1}
                <input type="hidden" name="post" value={this.state.post.id}></input>
            </form>
            );
        }
    }
}

export {CommentForm};