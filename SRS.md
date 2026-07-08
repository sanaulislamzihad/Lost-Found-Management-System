# Software Requirements Specification
## Lost & Found Management System

Prepared by
- Md Sanaul Islam Zihad - 2311774042
- Shahed Mehbub Shourov - 2231427042
- Jannatun Ferdousi - 2232429043
- Natasha Anwar – 2233128642

North South University
Software Engineering (CSE - 327)
7 July 2026

---

## Revision History

| Revision | Date | Author(s) | Description |
|---------|------|-----------|-------------|
| 1.0 | 07.07.2026 | Md Sanaul Islam Zihad | Initial draft — Introduction and Overall Description, Added Functional and Non-Functional Requirements, Added Glossary and final formatting |

---

## Table of Contents
1. Chapter 1: Introduction
2. Chapter 2: Overall Description
3. Chapter 3: Requirements
4. Appendix A: Glossary

---

# Chapter 1: Introduction

Lost personal belongings are a common and recurring problem on university and workplace campuses. Items such as ID cards, wallets, phones, books, and electronic accessories are frequently misplaced, and there is currently no centralized, reliable way for a person who has lost an item to connect with a person who has found it. This often results in permanently lost belongings, wasted time, and unnecessary frustration for students, staff, and campus security personnel. If this process could be digitized and centralized, the effort required to reunite lost items with their owners would be significantly reduced.

## 1.1 Purpose

To create a "Lost & Found Management System" web application that allows students and staff to report lost items, report found items, search and filter existing reports by category, location, and date, upload images of items, and claim items that belong to them. The system also provides a verification workflow so that a Security Officer can approve or reject claims before an item is handed over, and gives an Admin the tools to manage users, posts, categories, and reports across the platform.

## 1.2 Intended Audience

- Developers
- Project Testers
- University IT / Security Administration

## 1.3 Intended Use

- Developers:
  Developers can use this SRS to understand the scope of the project, which modules require the most attention, which parts can be improved, and whether there is room to add new features in future iterations.
- Project Testers:
  Testers can use this SRS to test the software against the stated requirements. This makes testing more organized, since testers can identify exactly where to look and what kind of errors or bugs to search for.
- University IT / Security Administration:
  The security and administrative staff can use this SRS to understand how claim verification works and how the system helps reduce fraudulent or unauthorized claims of lost items.

## 1.4 Product Scope

This is a completely new, web-based application built from scratch to help students, staff, and security personnel manage lost and found items across a campus or organization.

Benefits of this web application:
1. A user can report a lost item with details such as category, description, location, and date.
2. A user can report a found item so that the rightful owner can be notified.
3. A user can search and filter lost/found items by category, location, or date.
4. A user can upload an image of the item to help with identification.
5. A user can submit a claim for an item that belongs to them.
6. A Security Officer can verify claims and approve or reject them before an item is released.
7. Users receive notifications when a claim is approved/rejected or when a new item matching their report is posted.
8. An Admin can manage users, item posts, categories, and generate reports.

Objective of our web application is to:
1. Give the campus community a centralized, reliable channel to report and recover lost items.
2. Reduce the time and effort required to reunite an owner with a lost item.

Goals:
1. Our goal is to ensure that no lost item goes unclaimed due to a lack of communication between the finder and the owner.
2. We are providing an online platform so that users can report and search for items instantly, from anywhere.
3. Security verification ensures that items are only released to their rightful owners, preventing fraudulent claims.

## 1.5 Risk Definition

1. For an unstable network connection, uploading images or submitting reports can fail or be delayed.
2. A large number of simultaneous claim requests may be difficult for the Security Officer to process in a timely manner.
3. Too many users accessing the system at the same time can cause server traffic and slow response times.
4. Users may submit false claims for items that do not belong to them.

---

# Chapter 2: Overall Description

We are going to build a web-based application that provides a centralized platform for reporting, searching, and claiming lost and found items. It will serve as a common platform for item owners, item finders, security personnel who verify claims, and administrators who oversee the platform. This is a completely new product, built from scratch.

## 2.1 User Classes and Characteristics

This web-based application helps students and staff who have lost an item, or who have found an item belonging to someone else. The application is designed to be simple and intuitive so that anyone on campus can use it without prior training.

- User can be a Student.
- User can be a member of Staff.
- User can be a Security Officer responsible for verifying and approving claims.
- User can be an Admin responsible for managing the overall platform.

## 2.2 User Needs

Students and staff will use this application whenever they lose or find an item on campus. If they need to report a lost item, report a found item, search existing posts, or claim an item, they can do so through this system. They also need to be notified when their claim is approved or rejected, or when a new item is posted that matches the category of something they reported as lost. On the other hand, Security Officers need a simple way to review pending claims and verify the rightful owner before releasing an item, and Admins need tools to manage users, posts, categories, and generate reports on system activity.

## 2.3 Operating Environment

- Operating system: Any operating system that supports a modern web browser.
- Database: SQLite (development), with the option to migrate to PostgreSQL for production.
- Platform: Python, Django Framework.

## 2.4 Constraints

- The application has to be developed using the Python / Django framework.
- The developed system must be accessible from any standard web browser on Windows, macOS, and mobile devices.
- The project has to be completed within one academic semester.

## 2.5 Assumptions

- Users can read and write English.
- Users have devices that support internet browsing (desktop or mobile).
- Users have a stable internet connection.
- Users are familiar with basic web navigation and can interact with a standard website.

---

# Chapter 3: Requirements

## 3.1 Functional Requirements

Functional requirements are grouped into nine modules below. Each requirement follows the user-story format (As a / I want / so that), and every requirement's Confirmation section lists the exact, testable acceptance criteria a developer or tester must verify before the requirement is considered complete.

### 3.1.1 Authentication Requirements

#### FR-1.1
As a user (Student / Staff), I want to register an account on the system so that I can securely access lost and found services under my own identity.

Confirmation (Acceptance Criteria):
- User has to provide full name, university/employee ID, email, and password to register.
- System must validate that the email is a valid, unused email address.
- Password must meet minimum strength requirements (e.g. at least 8 characters).
- User must verify their email address before the account is activated.
- Duplicate registration with the same ID or email must be rejected with an error message.

#### FR-1.2
As a registered user, I want to log in and log out of the system so that I can access my account securely and end my session when done.

Confirmation (Acceptance Criteria):
- User can log in using their registered email and password.
- System will show a clear error message for incorrect login credentials.
- System will lock the account temporarily after multiple failed login attempts.
- User can log out, which ends the active session immediately.
- User can reset a forgotten password via a verification link sent to their email.

### 3.1.2 Lost Item Management Requirements

#### FR-2.1
As a user, I want to report a lost item so that other users or the finder can help me get it back.

Confirmation (Acceptance Criteria):
- User has to enter item name, category, description, last known location, and date lost.
- User can optionally upload one or more photos of the item.
- System will validate that all mandatory fields are filled before submission.
- System will save the report with status "Pending" and display it in the browse list.
- User will get a notification if a matching found item is later reported.

#### FR-2.2
As a user, I want to edit or delete my own lost item report so that I can correct mistakes or remove the post once the item is recovered.

Confirmation (Acceptance Criteria):
- User can only edit or delete reports that they personally created.
- System will show a confirmation prompt before deleting a report.
- System will mark a recovered item's report as "Resolved" instead of only deleting it, to keep history.

### 3.1.3 Found Item Management Requirements

#### FR-3.1
As a user, I want to report a found item so that the rightful owner can be notified and reclaim their belonging.

Confirmation (Acceptance Criteria):
- User has to enter item name, category, description, location found, and date found.
- User can optionally upload one or more photos of the item.
- System will validate that all mandatory fields are filled before submission.
- System will save the report with status "Available" and display it in the browse list.
- User will be notified when someone submits a claim for the item.

#### FR-3.2
As a user, I want to edit or delete my own found item report so that I can keep the listing accurate or remove it once the item is returned.

Confirmation (Acceptance Criteria):
- User can only edit or delete reports that they personally created.
- System will automatically mark a found item's report as "Claimed" once a claim is approved.
- System will show a confirmation prompt before deleting a report.

### 3.1.4 Search & Filter Requirements

#### FR-4.1
As a user, I want to search lost and found items by keyword so that I can quickly check if my item has already been found or reported.

Confirmation (Acceptance Criteria):
- User can search by item name, category, or description keyword.
- System will display a list of matching lost/found posts within 3 seconds.
- User can click on a post to view full details, including image and status.
- System will display "No results found" when a search returns nothing.

#### FR-4.2
As a user, I want to filter items by category, location, or date so that I can narrow down results and find relevant items quickly.

Confirmation (Acceptance Criteria):
- User can select one or more filters: category, location, and date range.
- System will update the results list dynamically based on the selected filters.
- Filters can be combined with the keyword search from FR-4.1.
- User can clear all filters to return to the full, unfiltered list.

### 3.1.5 Item Claim Requirements

#### FR-5.1
As a user, I want to claim an item so that I can retrieve my lost item from the finder or security office.

Confirmation (Acceptance Criteria):
- User has to select the found item post and submit a claim request.
- User has to provide proof of ownership details (e.g. a unique mark, purchase receipt, or ID match).
- System will not allow a user to submit more than one active claim on the same item.
- System will forward the claim request to the Security Officer for verification with status "Pending".
- User will be notified once the claim is approved or rejected.

#### FR-5.2
As a Security Officer, I want to verify claims and approve or reject them so that items are only released to their rightful owners.

Confirmation (Acceptance Criteria):
- Security Officer can view a list of all pending claim requests, sorted by submission date.
- Security Officer can review the claimant's proof of ownership against the item's stored details.
- Security Officer can approve or reject a claim, with a mandatory remark when rejecting.
- Approving a claim automatically updates the item's status to "Claimed" and closes other pending claims on it.
- System will automatically notify the claimant of the final decision.

### 3.1.6 Notification Requirements

#### FR-6.1
As a user, I want to receive notifications about my activity so that I stay updated about my reports, claims, and matching items without checking manually.

Confirmation (Acceptance Criteria):
- System will notify the user when their claim is approved or rejected.
- System will notify the user when a new found item matching their lost report's category is posted.
- System will notify the finder when someone submits a claim on their found item post.
- Notifications will be visible inside the application in a dedicated notifications panel.
- User can optionally enable an email copy of each notification.

### 3.1.7 User Profile Requirements

#### FR-7.1
As a registered user, I want to view and edit my profile information so that my contact details stay accurate and I control what others can see.

Confirmation (Acceptance Criteria):
- User can view their name, ID, email, and phone number on a profile page.
- User can edit their phone number and profile photo; email/ID remain fixed after registration.
- System will validate new data before saving changes.

#### FR-7.2
As a registered user, I want to view the history of my own lost/found reports and claims so that I can track the status of everything I have posted or claimed.

Confirmation (Acceptance Criteria):
- User can view a list of all lost/found items they have reported, with current status.
- User can view a list of all claims they have submitted, with approval/rejection status.
- List can be filtered by status: Pending, Available, Claimed, Resolved.

### 3.1.8 Admin Dashboard Requirements

#### FR-8.1
As an Admin, I want to manage user accounts so that I can keep the platform's user base accurate and safe.

Confirmation (Acceptance Criteria):
- Admin can view a list of all registered users with their role and status.
- Admin can activate, deactivate, or delete a user account.
- Admin can assign or change a user's role (Student, Staff, Security Officer, Admin).

#### FR-8.2
As an Admin, I want to manage item posts and categories so that the platform remains organized and free of duplicate or inappropriate content.

Confirmation (Acceptance Criteria):
- Admin can view, edit, or remove any lost/found item post.
- Admin can add, edit, or remove item categories.
- Admin can review posts flagged as inappropriate by other users and take action (approve/remove).

#### FR-8.3
As an Admin, I want to view system-wide reports and statistics so that I can monitor overall platform activity and performance.

Confirmation (Acceptance Criteria):
- Admin can view total counts of lost items, found items, and successful claims.
- Admin can view claim approval/rejection statistics over a selected date range.
- Admin can export activity reports (e.g. as CSV or PDF).

### 3.1.9 Database Requirements

These requirements describe how the system's core data must be structured and stored to correctly support the modules above.

- The system shall maintain a Users table storing name, ID, email, hashed password, role, and account status.
- The system shall maintain an Items table storing item name, category, description, location, date, type (lost/found), status, and image reference for each report, linked to the reporting user.
- The system shall maintain a Categories table used to classify items (e.g. Electronics, Documents, Accessories, Bags).
- The system shall maintain a Claims table linking a claimant, an item, proof-of-ownership details, verification status, and the reviewing Security Officer.
- The system shall maintain a Notifications table logging each notification sent to a user, with a read/unread flag.
- The database shall enforce referential integrity between Users, Items, Claims, and Categories (e.g. an item cannot reference a non-existent category).
- Uploaded images shall be stored in a dedicated media directory/storage service, with only the file path saved in the database.

## 3.2 Non-Functional Requirements

### Performance Requirements
- The system must remain responsive under a high number of concurrent users without failure.
- Response to any user interaction must take no longer than 3 seconds to appear on screen.

### Security Requirements
- The system will use a secure database with hashed passwords.
- Normal users can only view and submit their own reports/claims; they cannot edit or delete other users' posts.
- Only the Security Officer role can approve or reject claim requests.

### Error Handling
- The system must handle expected and unexpected errors in a way that prevents data loss and minimizes downtime.

### Safety Requirements
- System use must not expose any user's private contact information to other users without consent.

---

# Appendix A: Glossary

- SRS: A software requirements specification (SRS) is a description of a software system to be developed. It lays out functional and non-functional requirements, and may include use cases describing user interactions the software must support.
- Claim Verification: The process by which a Security Officer confirms that a person requesting a found item is its rightful owner before the item is released.
- Category: A classification tag (e.g. Electronics, Documents, Accessories, Bags) used to group similar lost or found items for easier searching and filtering.
- QR Code Verification: An optional feature where a unique QR code is generated for an approved claim, which can be scanned at the security office to confirm and finalize the handover of an item.
