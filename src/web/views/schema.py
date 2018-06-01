import json
from flask import Blueprint, render_template, redirect, url_for, flash, \
                    request, abort
from flask_login import login_required, current_user
from flask_babel import gettext
from sqlalchemy import or_

from bootstrap import db
from web.forms import SchemaForm
from web.models import Schema, JsonObject, Organization

schema_bp = Blueprint('schema_bp', __name__, url_prefix='/schema')
schemas_bp = Blueprint('schemas_bp', __name__, url_prefix='/schemas')


@schemas_bp.route('/', methods=['GET'])
def list_shemas():
    """Return the page which will display the list of schemas."""
    return render_template('schemas.html')


@schema_bp.route('/<int:schema_id>', methods=['GET'])
def get(schema_id=None):
    """Return the schema given in parameter with the objects validated by this
    schema."""
    schema = Schema.query.filter(Schema.id == schema_id).first()
    if schema is None:
        abort(404)
    if not current_user.is_authenticated:
        # Loads public objects related to the schema
        objects = JsonObject.query. \
                filter(JsonObject.schema_id==schema.id). \
                filter(JsonObject.is_public)
    elif current_user.is_admin:
        # Loads all objects related to the schema
        objects = JsonObject.query.filter(JsonObject.schema_id==schema.id)
    else:
        # Loads objects related to the schema that are:
        #   - public;
        #   - private but related to the organizations the current user is
        #     affiliated to.
        objects = JsonObject.query. \
                filter(JsonObject.schema_id==schema.id). \
                filter(or_(JsonObject.is_public,
                            JsonObject.organization. \
                                has(Organization.id.in_([org.id for org in current_user.organizations]))))
    return render_template('schema.html', schema=schema, objects=objects)


@schema_bp.route('/create', methods=['GET'])
@schema_bp.route('/edit/<int:schema_id>', methods=['GET'])
@login_required
def form(schema_id=None, org_id=None):
    action = "Create a schema"
    head_titles = [action]

    form = SchemaForm()
    form.org_id.choices = [(0, '')]
    form.org_id.choices.extend([(org.id, org.name) for org in
                                                    current_user.organizations])

    if schema_id is None:
        org_id = request.args.get('org_id', None)
        if org_id is not None:
            form.org_id.data = int(org_id)
        return render_template('edit_schema.html', action=action,
                               head_titles=head_titles, form=form)

    schema = Schema.query.filter(Schema.id == schema_id).first()
    form = SchemaForm(obj=schema)
    form.org_id.choices = [(0, '')]
    form.org_id.choices.extend([(org.id, org.name) for org in
                                                    current_user.organizations])
    action = "Edit an object"
    head_titles = [action]
    head_titles.append(schema.name)
    return render_template('edit_schema.html', action=action,
                           head_titles=head_titles, schema=schema, form=form)


@schema_bp.route('/create', methods=['POST'])
@schema_bp.route('/edit/<int:schema_id>', methods=['POST'])
@login_required
def process_form(schema_id=None):
    form = SchemaForm()
    form.org_id.choices = [(0, '')]
    form.org_id.choices.extend([(org.id, org.name) for org in
                                                    current_user.organizations])

    if not form.validate():
        return render_template('edit_schema.html', form=form)

    # Edit an existing schema
    if schema_id is not None:
        schema = Schema.query.filter(Schema.id == schema_id).first()
        form.populate_obj(schema)
        try:
            db.session.commit()
            flash(gettext('%(object_name)s successfully updated.',
                    object_name=form.name.data), 'success')
        except Exception as e:
            print(e)
            form.name.errors.append('Name already exists.')
        return redirect(url_for('schema_bp.form', schema_id=schema.id))

    # Create a new schema
    schema_json_obj = json.loads(form.json_schema.data)
    new_schema = Schema(name=form.name.data,
                        description=form.description.data,
                        json_schema=schema_json_obj,
                        org_id=form.org_id.data,
                        creator_id=current_user.id)
    db.session.add(new_schema)
    try:
        db.session.commit()
        flash(gettext('%(object_name)s successfully created.',
                object_name=new_schema.name), 'success')
    except Exception as e:
        # TODO: display the error
        return redirect(url_for('schema_bp.form', schema_id=new_schema.id))
    return redirect(url_for('schema_bp.form', schema_id=new_schema.id))
