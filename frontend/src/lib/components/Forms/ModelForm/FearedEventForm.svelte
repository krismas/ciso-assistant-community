<script lang="ts">
	import type { SuperValidated } from 'sveltekit-superforms';
	import type { ModelInfo, CacheLock } from '$lib/utils/types';
	import TextField from '$lib/components/Forms/TextField.svelte';
	import AutocompleteSelect from '$lib/components/Forms/AutocompleteSelect.svelte';
	import Select from '$lib/components/Forms/Select.svelte';
	import { m } from '$paraglide/messages';
	import TextArea from '../TextArea.svelte';
	import Checkbox from '$lib/components/Forms/Checkbox.svelte';

	export let form: SuperValidated<any>;
	export let model: ModelInfo;
	export let cacheLocks: Record<string, CacheLock> = {};
	export let formDataCache: Record<string, any> = {};
	export let initialData: Record<string, any> = {};
</script>

<p class="text-sm text-gray-500">{m.fearedEventHelpText()}</p>
<AutocompleteSelect
	{form}
	field="ebios_rm_study"
	cacheLock={cacheLocks['ebios_rm_study']}
	bind:cachedValue={formDataCache['ebios_rm_study']}
	label={m.ebiosRmStudy()}
	hidden={initialData.ebios_rm_study}
/>
<AutocompleteSelect
	{form}
	field="folder"
	cacheLock={cacheLocks['folder']}
	bind:cachedValue={formDataCache['folder']}
	label={m.folder()}
	hidden
/>
<TextField
	{form}
	field="ref_id"
	label={m.refId()}
	cacheLock={cacheLocks['ref_id']}
	bind:cachedValue={formDataCache['ref_id']}
/>
<Select
	{form}
	options={model.selectOptions['gravity']}
	field="gravity"
	label={m.gravity()}
	cacheLock={cacheLocks['gravity']}
	bind:cachedValue={formDataCache['gravity']}
	helpText={m.gravityHelpText()}
/>
<TextArea
	{form}
	field="justification"
	label={m.justification()}
	cacheLock={cacheLocks['justification']}
	bind:cachedValue={formDataCache['justification']}
/>
<AutocompleteSelect
	multiple
	{form}
	optionsEndpoint="assets?type=PR"
	optionsDetailedUrlParameters={[['ebios_rm_studies', initialData.ebios_rm_study]]}
	optionsExtraFields={[['folder', 'str']]}
	optionsLabelField="auto"
	field="assets"
	label={m.assets()}
	helpText={m.fearedEventAssetHelpText()}
/>
<AutocompleteSelect
	multiple
	{form}
	optionsEndpoint="qualifications"
	field="qualifications"
	label={m.qualifications()}
	helpText={m.fearedEventQualificationHelpText()}
/>
<Checkbox
	{form}
	field="is_selected"
	label={m.isSelected()}
	helpText={m.fearedEventIsSelectedHelpText()}
/>
