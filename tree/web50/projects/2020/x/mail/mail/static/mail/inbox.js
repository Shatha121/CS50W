document.addEventListener('DOMContentLoaded', function() {
    // Use buttons to toggle between views
    document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
    document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
    document.querySelector('#compose').addEventListener('click', compose_email);
  
    // By default, load the inbox
    load_mailbox('inbox');
  });
  
  function compose_email(recipients = '', subject = '', body = '') {
    // Show compose view and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'block';
  
    // Clear out composition fields or pre-fill them if provided
    document.querySelector('#compose-recipients').value = recipients;
    document.querySelector('#compose-subject').value = subject;
    document.querySelector('#compose-body').value = body;
  
    // Handle form submission
    document.querySelector('#compose-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission
  
        fetch('/emails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipients: document.querySelector('#compose-recipients').value,
                subject: document.querySelector('#compose-subject').value,
                body: document.querySelector('#compose-body').value
            })
        })
        .then(response => response.json())
        .then(result => {
            console.log("Email sent:", result);
            load_mailbox('sent'); // Load the sent mailbox after sending the email
        })
        .catch(error => {
            console.error("Error sending email:", error);
        });
    }, { once: true }); // Ensure the event listener is added only once
  }
  
  function load_mailbox(mailbox) {
    // Show the mailbox and hide other views
    document.querySelector('#emails-view').style.display = 'block';
    document.querySelector('#compose-view').style.display = 'none';
  
    // Show the mailbox name
    document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
    // Fetch emails for the selected mailbox
    fetch(`/emails/${mailbox}`)
        .then(response => response.json())
        .then(emails => {
            // Clear existing emails
            const emailsView = document.querySelector('#emails-view');
            emailsView.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
            // Append emails to the view
            emails.forEach(email => {
                const emailElement = document.createElement('div');
                emailElement.className = 'email';
                emailElement.style.border = '1px solid #ddd'; // Add border
                emailElement.style.padding = '10px'; // Add padding
                emailElement.style.marginBottom = '10px'; // Add margin between emails
  
                // Add background color based on read/unread status
                emailElement.style.backgroundColor = email.read ? '#f5f5f5' : '#fff';
  
                emailElement.innerHTML = `
                    <strong>From: ${email.sender}</strong><br>
                    <strong>Subject: ${email.subject}</strong><br>
                    <small>${email.timestamp}</small><br>
                    <button class="btn btn-primary" data-id="${email.id}">View</button>
                `;
                emailsView.appendChild(emailElement);
            });
  
            // Attach event listeners to each view button
            document.querySelectorAll('.btn-primary').forEach(button => {
                button.addEventListener('click', function() {
                    const emailId = this.dataset.id;
                    
                    // Mark email as read
                    fetch(`/emails/${emailId}`, {
                        method: 'PUT',
                        body: JSON.stringify({
                            read: true
                        })
                    });
  
                    // Fetch and display the email
                    fetch(`/emails/${emailId}`)
                        .then(response => response.json())
                        .then(email => {
                            const emailsView = document.querySelector('#emails-view');
                            emailsView.innerHTML = `
                                <h3>${email.subject}</h3>
                                <p><strong>From:</strong> ${email.sender}</p>
                                <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
                                <p><strong>Timestamp:</strong> ${email.timestamp}</p>
                                <hr>
                                <p>${email.body}</p>
                                <button class="btn btn-secondary" id="back">Back</button>
                                ${mailbox === 'inbox' ? `<button class="btn btn-warning" id="archive">Archive</button>` : ''}
                                ${mailbox === 'archive' ? `<button class="btn btn-warning" id="unarchive">Unarchive</button>` : ''}
                                <button class="btn btn-primary" id="reply">Reply</button>
                            `;
                            
                            // Add back button functionality
                            document.querySelector('#back').addEventListener('click', () => load_mailbox(mailbox));
  
                            // Archive or Unarchive functionality
                            if (mailbox === 'inbox') {
                                document.querySelector('#archive').addEventListener('click', function() {
                                    fetch(`/emails/${emailId}`, {
                                        method: 'PUT',
                                        body: JSON.stringify({
                                            archived: true
                                        })
                                    })
                                    .then(() => load_mailbox('inbox')); // Reload inbox after archiving
                                });
                            } else if (mailbox === 'archive') {
                                document.querySelector('#unarchive').addEventListener('click', function() {
                                    fetch(`/emails/${emailId}`, {
                                        method: 'PUT',
                                        body: JSON.stringify({
                                            archived: false
                                        })
                                    })
                                    .then(() => load_mailbox('inbox')); // Reload inbox after unarchiving
                                });
                            }
  
                            // Reply functionality
                            document.querySelector('#reply').addEventListener('click', function() {
                                // Pre-fill the composition form
                                let subject = email.subject;
                                if (!subject.startsWith('Re:')) {
                                    subject = `Re: ${subject}`;
                                }
  
                                const body = `On ${email.timestamp}, ${email.sender} wrote:\n${email.body}\n\n`;
                                
                                compose_email(email.sender, subject, body);
                            });
                        })
                        .catch(error => {
                            console.error('Error loading email:', error);
                        });
                });
            });
        })
        .catch(error => {
            console.error('Error loading mailbox:', error);
        });
  }
  