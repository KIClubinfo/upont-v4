import { render } from 'react-dom';
import { Students } from '../components/StudentsPage/StudentsComponent';

//@ts-ignore window.react_mount is declared in django template
render(<Students />, window.react_mount);
