# Digital Memobook Frontend

Welcome to the Digital Memobook frontend repository! This project provides a user-friendly interface for managing user profiles, photos, and journals.

## Features

- **User Profile:**
  - Display user profile information.
  - Edit user profile details.

- **User Photos:**
  - Display user photos.
    - [x] get_photos(, filter)
      - [ ] back_end 
  - Delete user photos.
    - delete_photos()
  - Edit photo details.
    - update_photo()
      - [ ] Add `edit` button
  - Upload photo
    - [ ] upload_photos()
    - [ ] analyze_photos()
  - Generate journal.
    - [ ] generate journal backend

- **User Journals:**
  - Display user journals.
    - [x] get_journals(, filter)
  - Edit journal entries.
    - [ ] update_journal()
  - Delete journal entries.
    - [ ] delete_journals()


## Usage

1. **Development Mode:**
   ```bash
   npm run dev
   ```
   This command starts the development server.

2. **Production Build:**
   ```bash
   npm run build
   ```
   This command generates a production build in the `build` folder.

3. **Deployment:**
   - Deploy the contents of the `build` folder to your preferred hosting service.

## Technologies Used

- React.js
- Axios (for API requests)
- React Router (for routing)
- Tailwind CSS (for styling)

## Contributing

Contributions are welcome! Please fork this repository and submit pull requests to propose changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Feel free to customize this README to fit your specific project structure and additional features.