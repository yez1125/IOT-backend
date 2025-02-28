# Heart Chain

## Overview

Heart Chain is a privacy-focused mental health support platform that provides users with an anonymous way to express their feelings, consult with counselors, and complete tasks to improve their well-being. The platform includes various features such as diary logging, anonymous counseling, meeting rooms, and a psychological token system.

## Features

- **Anonymous Counseling**: Users can schedule anonymous consultation sessions and join secure virtual meetings.
- **Diary Chatbot**: A chatbot-based diary where users can write and receive supportive feedback.
- **Tasks & Rewards**: Users can complete wellness-related tasks and earn psychological tokens.
- **Questionnaire**: A section to assess mental health status through simple questionnaires.
- **Meeting Room**: Secure video conferencing for counseling sessions.

## Installation

To set up the project locally, follow these steps:

### Prerequisites

Ensure you have the following installed:

- Node.js (v14 or later)
- npm or yarn

### Steps

1. Clone the repository:

   ```sh
   git clone https://github.com/your-repo/heart-chain.git
   cd heart-chain
   ```

2. Install dependencies:

   ```sh
   npm install
   ```

3. Start the development server:

   ```sh
   npm start
   ```

   This will launch the application on http://localhost:3000/.

## Folder Structure

```
/heart-chain
├── src
│   ├── components       # UI components
│   ├── pages            # Main pages
│   ├── App.jsx          # Root component
│   ├── PageRouter.jsx   # Routing configuration
│   ├── index.jsx        # Entry point
│   ├── styles           # CSS files
│   └── assets           # Static assets
├── public               # Public assets
├── package.json         # Project dependencies
├── README.md            # Project documentation
```

## Pages & Routes

- `/` - **Home**
  - Introduction to the platform
  - Call-to-action button to start counseling

- `/diary` - **Diary Chatbot**
  - Allows users to chat with a bot and log emotions
  - Suggests professional help if needed

- `/counsel` - **Anonymous Counseling**
  - Users can book a time slot for counseling
  - Secure anonymous environment

- `/meeting-room` - **Meeting Room**
  - Secure video meeting for users and counselors
  - Camera selection and session controls

- `/tasks` - **Tasks & Rewards**
  - Users complete wellness tasks
  - Progress tracking with a reward system

- `/questionnaire` - **Mental Health Assessment**
  - Users answer mental health-related questions
  - Helps assess emotional well-being

## Technologies Used

- **deep-live-cam**: Privacy protection for video streaming, url: https://github.com/hacksider/Deep-Live-Cam
- **React**: Frontend framework
- **React Router**: Navigation
- **Bootstrap**: UI styling
